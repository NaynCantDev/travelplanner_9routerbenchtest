import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
from commonsense_constraint import evaluation as commonsense_eval
from hard_constraint import evaluation as hard_eval
import json
from tqdm import tqdm
from datasets import load_dataset
import argparse


def load_line_json_data(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.read().strip().split('\n'):
            unit = json.loads(line)
            data.append(unit)
    return data

def count_true_false(data):
    """Count the number of true and false values in a list."""
    true_count = data.count(True)
    false_count = data.count(False)
    return true_count, false_count

def statistics(commonsense_statistic):
    """Generate statistics for each level and day in the given data with a different structure."""
    result = {level: {day: {} for day in commonsense_statistic[level]} for level in commonsense_statistic}
    
    for level, days in commonsense_statistic.items():
        for day, dicts in days.items():
            for dct in dicts:
                if dct:
                    for key, data in dct.items():
                        true_count, false_count = count_true_false(data)
                        if key not in result[level][day]:
                            result[level][day][key] = {"true": 0, "false": 0}
                        result[level][day][key]["true"] += true_count
                        result[level][day][key]["false"] += false_count
                
    return result

def paper_term_mapping(commonsense_constraint_record, hard_constraint_record):
    mapping_dict = {'is_valid_information_in_current_city':'Within Current City','is_valid_information_in_sandbox':'Within Sandbox','is_reasonable_visiting_city':'Reasonable City Route','is_valid_restaurants':'Diverse Restaurants','is_valid_transportation':'Non-conf. Transportation','is_valid_attractions':'Diverse Attractions','is_valid_accommodation':'Minimum Nights Stay','is_not_absent':'Complete Information','valid_cost':'Budget','valid_room_rule':'Room Rule','valid_cuisine':'Cuisine','valid_room_type':'Room Type','valid_transportation':'Transportation'}
    remap_commonsense_constraint_record = {level:{day:{} for day in [3,5,7]} for level in ['easy','medium','hard']} 
    remap_hard_constraint_record = {level:{day:{} for day in [3,5,7]} for level in ['easy','medium','hard']} 
    for level in commonsense_constraint_record:
        for day in commonsense_constraint_record[level]:
            remap_commonsense_constraint_record[level][day] = {mapping_dict[key] : val for key,val in commonsense_constraint_record[level][day].items()}
            remap_hard_constraint_record[level][day] = {mapping_dict[key] : val for key,val in hard_constraint_record[level][day].items()}
    return remap_commonsense_constraint_record, remap_hard_constraint_record


def parse_query_indices(query_indices, max_len=None):
    if not query_indices:
        return list(range(1, max_len + 1)) if max_len else []
    indices = []
    for part in query_indices.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start, end = map(int, part.split('-'))
            indices.extend(range(start, end + 1))
        else:
            indices.append(int(part))
    indices = sorted(list(set(indices)))
    if max_len:
        indices = [i for i in indices if 1 <= i <= max_len]
    return indices


def eval_score(set_type: str, file_path: str, query_indices: str = None, return_per_query: bool = False):

    if set_type == 'train':
        query_data_list  = load_dataset('osunlp/TravelPlanner','train',download_mode="force_redownload")['train']
    elif set_type == 'validation':
        query_data_list  = load_dataset('osunlp/TravelPlanner','validation',download_mode="force_redownload")['validation']

    query_data_list = [x for x in query_data_list]
    hardConstraint_statistic= {level:{day:[] for day in [3,5,7]} for level in ['easy','medium','hard']} 
    commonsenseConstraint_statistic = {level:{day:[] for day in [3,5,7]} for level in ['easy','medium','hard']} 
    tested_plans_raw = load_line_json_data(file_path)
    tested_plans_map = {}
    for item in tested_plans_raw:
        if isinstance(item, str):
            try:
                item = json.loads(item)
            except Exception:
                try:
                    item = eval(item)
                except Exception:
                    continue
        if isinstance(item, dict) and 'idx' in item:
            tested_plans_map[item['idx']] = item

    if query_indices:
        target_indices = parse_query_indices(query_indices, len(query_data_list))
    else:
        target_indices = list(range(1, len(query_data_list) + 1))

    delivery_cnt = 0
    plan_constraint_store = []
    for q_idx in tqdm(target_indices, desc="Evaluating plans"):
        query_data = query_data_list[q_idx - 1]
        tested_plan = tested_plans_map.get(q_idx)
        if tested_plan is None and (q_idx - 1) < len(tested_plans_raw):
            tested_plan = tested_plans_raw[q_idx - 1]
            if isinstance(tested_plan, str):
                try:
                    tested_plan = json.loads(tested_plan)
                except Exception:
                    tested_plan = eval(tested_plan)
        if tested_plan is None:
            tested_plan = {'idx': q_idx, 'plan': None}

        if type(query_data) == str:
            query_data = eval(query_data)
        if type(query_data['local_constraint']) == str:
            query_data['local_constraint'] = eval(query_data['local_constraint'])

        is_delivered = False
        if tested_plan.get('plan') and isinstance(tested_plan['plan'], list) and len(tested_plan['plan']) > 0:
            if all(isinstance(day, dict) and 'current_city' in day for day in tested_plan['plan']):
                is_delivered = True

        if is_delivered:
            delivery_cnt += 1
            commonsense_info_box = commonsense_eval(query_data,tested_plan['plan'])
        else:
            commonsense_info_box = None

        if commonsense_info_box and commonsense_info_box['is_not_absent'][0] and commonsense_info_box['is_valid_information_in_sandbox'][0]:
            hard_info_box = hard_eval(query_data,tested_plan['plan'])
        else:
            hard_info_box = None

        plan_constraint_store.append({'commonsense_constraint':commonsense_info_box,'hard_constraint':hard_info_box})

        commonsenseConstraint_statistic[query_data['level']][query_data['days']].append(commonsense_info_box)
        hardConstraint_statistic[query_data['level']][query_data['days']].append(hard_info_box)

    constraint_record = {key: {day: {'house rule':0, 'cuisine':0, 'room type':0, 'transportation':0} for day in [3,5,7]} for key in ['medium','hard']}
    constraint_mapping = {'house rule':'valid_room_rule','cuisine':'valid_cuisine','room type':'valid_room_type','transportation':'valid_transportation'}
    mapping_constraint_record = {key: {day: {'valid_room_rule':0, 'valid_cuisine':0, 'valid_room_type':0, 'valid_transportation':0} for day in [3,5,7]} for key in ['medium','hard']}
    count_record = {key:{day:0 for day in [3,5,7]} for key in ['easy','medium','hard']}

    for q_idx in target_indices:
        unit = query_data_list[q_idx - 1]
        count_record[unit['level']][unit['days']] += 1
        for key in constraint_record['medium'][3]:
            if unit['local_constraint'][key] != None:
                constraint_record[unit['level']][unit['days']][key] += 1
                mapping_constraint_record[unit['level']][unit['days']][constraint_mapping[key]] += 1
    
    commonsenseConstraint_statistic_processed = statistics(commonsenseConstraint_statistic)
    hardConstraint_statistic_processed = statistics(hardConstraint_statistic)


    data_record = {key:{day:[] for day in [3,5,7]} for key in ['easy','medium','hard']}

    constraint_dis_record = {"commonsense":{"pass":0,"total":0},"hard":{"pass":0,"total":0}}
    constraint_count = {key:{day:{} for day in [3,5,7]} for key in ['easy','medium','hard']}

    for constraint in ['commonsense','hard']:
        if constraint == 'commonsense':
            constraint_statistic = commonsenseConstraint_statistic_processed
        elif constraint == 'hard':
            constraint_statistic = hardConstraint_statistic_processed

        key_dict = {'commonsense':['is_valid_information_in_current_city','is_valid_information_in_sandbox','is_reasonable_visiting_city','is_valid_restaurants','is_valid_transportation','is_valid_attractions','is_valid_accommodation','is_not_absent'],'hard':['valid_cost','valid_room_rule','valid_cuisine','valid_room_type','valid_transportation']}
        
        for key in constraint_statistic:
            for key2 in constraint_statistic[key]:
                if key2 == -1:
                    print(constraint_statistic[key])
                    exit(0)
                for key3 in key_dict[constraint]:
                    data_record[key][key2].append('0/0')
                    if key3 in constraint_statistic[key][key2]:
                        constraint_dis_record[constraint]['pass'] += constraint_statistic[key][key2][key3]['true']
                        if constraint == 'hard':
                            if key == 'hard' and key3 in ['valid_room_rule','valid_cuisine','valid_room_type','valid_transportation']:
                                data_record[key][key2][-1] = f"{constraint_statistic[key][key2][key3]['true']}/{mapping_constraint_record[key][key2][key3]}"
                                constraint_dis_record[constraint]['total'] += mapping_constraint_record[key][key2][key3]
                                hardConstraint_statistic_processed[key][key2][key3]['total'] = mapping_constraint_record[key][key2][key3]
                            elif key == 'medium' and key3 in ['valid_room_rule','valid_cuisine','valid_room_type']:
                                data_record[key][key2][-1] = f"{constraint_statistic[key][key2][key3]['true']}/{mapping_constraint_record[key][key2][key3]}"
                                constraint_dis_record[constraint]['total'] += mapping_constraint_record[key][key2][key3]
                                hardConstraint_statistic_processed[key][key2][key3]['total'] = mapping_constraint_record[key][key2][key3]
                            else:
                                data_record[key][key2][-1] = f"{constraint_statistic[key][key2][key3]['true']}/{count_record[key][key2]}"
                                if key3 in ['valid_cost','valid_visitng_city_number','valid_days']:
                                    constraint_dis_record[constraint]['total'] += count_record[key][key2]
                                    constraint_count[key][key2][key3] = count_record[key][key2]
                                    hardConstraint_statistic_processed[key][key2][key3]['total'] = count_record[key][key2]
                        else:
                            data_record[key][key2][-1] = f"{constraint_statistic[key][key2][key3]['true']}/{count_record[key][key2]}"
                            constraint_dis_record[constraint]['total'] += count_record[key][key2]
                            constraint_count[key][key2][key3] = count_record[key][key2]
                            commonsenseConstraint_statistic_processed[key][key2][key3]['total'] =  count_record[key][key2]
    final_all_cnt = 0
    final_commonsense_cnt = 0
    final_hardConstraint_cnt = 0
    final_all_cnt_map = {level:0 for level in ['easy','medium','hard']}
    per_query_results = []

    for store_idx, q_idx in enumerate(target_indices):
        query_data = query_data_list[q_idx - 1]
        cs_box = plan_constraint_store[store_idx]['commonsense_constraint']
        hd_box = plan_constraint_store[store_idx]['hard_constraint']
        is_delivered = bool(tested_plans_map.get(q_idx, {}).get('plan'))
        cs_pass = False
        hd_pass = False

        if cs_box:
            final_commonsense_pass = True
            final_hardConstraint_pass = True
            for item in cs_box:
                if cs_box[item][0] is not None and not cs_box[item][0]:
                    final_commonsense_pass = False
                    break
            if hd_box is None:
                final_hardConstraint_pass = False
            else:
                for item in hd_box:
                    if hd_box[item][0] is not None and hd_box[item][0] == False:
                        final_hardConstraint_pass = False
                        break
                
            if hd_box is not None:
                if final_commonsense_pass:
                    final_commonsense_cnt += 1
                if final_hardConstraint_pass:
                    final_hardConstraint_cnt += 1
                if final_commonsense_pass and final_hardConstraint_pass:
                    final_all_cnt += 1
                    final_all_cnt_map[query_data['level']] += 1
            cs_pass = final_commonsense_pass
            hd_pass = final_hardConstraint_pass

        per_query_results.append({
            "idx": q_idx,
            "level": query_data.get('level'),
            "days": query_data.get('days'),
            "delivered": is_delivered,
            "commonsense_pass": cs_pass,
            "hard_constraint_pass": hd_pass,
            "final_pass": cs_pass and hd_pass,
            "commonsense_details": {k: {"pass": v[0], "reason": v[1]} for k, v in cs_box.items()} if cs_box else None,
            "hard_details": {k: {"pass": v[0], "reason": v[1]} for k, v in hd_box.items()} if hd_box else None
        })

    result = {}

    remap_commonsense_constraint_record, remap_hard_constraint_record = paper_term_mapping(commonsenseConstraint_statistic_processed, hardConstraint_statistic_processed)

    if query_indices:
        total_eval = len(target_indices)
        result['Delivery Rate'] = delivery_cnt / total_eval
        cs_total = constraint_dis_record['commonsense']['total']
        result['Commonsense Constraint Micro Pass Rate'] = constraint_dis_record['commonsense']['pass'] / cs_total if cs_total > 0 else 0
        result['Commonsense Constraint Macro Pass Rate'] = final_commonsense_cnt / total_eval
        hard_total = constraint_dis_record['hard']['total']
        result['Hard Constraint Micro Pass Rate'] = constraint_dis_record['hard']['pass'] / hard_total if hard_total > 0 else 0
        result['Hard Constraint Macro Pass Rate'] = final_hardConstraint_cnt / total_eval
        result['Final Pass Rate'] = final_all_cnt / total_eval
    elif set_type == 'train':
        result['Delivery Rate'] = delivery_cnt / 45
        result['Commonsense Constraint Micro Pass Rate'] = constraint_dis_record['commonsense']['pass'] / 360
        result['Commonsense Constraint Macro Pass Rate'] = final_commonsense_cnt / 45
        result['Hard Constraint Micro Pass Rate'] = constraint_dis_record['hard']['pass'] / 105
        result['Hard Constraint Macro Pass Rate'] = final_hardConstraint_cnt / 45
        result['Final Pass Rate'] = final_all_cnt / 45

    elif set_type == 'validation':
        result['Delivery Rate'] = delivery_cnt / 180
        result['Commonsense Constraint Micro Pass Rate'] = constraint_dis_record['commonsense']['pass'] / 1440
        result['Commonsense Constraint Macro Pass Rate'] = final_commonsense_cnt / 180
        result['Hard Constraint Micro Pass Rate'] = constraint_dis_record['hard']['pass'] / 420
        result['Hard Constraint Macro Pass Rate'] = final_hardConstraint_cnt / 180
        result['Final Pass Rate'] = final_all_cnt / 180

    elif set_type == 'test':
        result['Delivery Rate'] = delivery_cnt / 1000
        result['Commonsense Constraint Micro Pass Rate'] = constraint_dis_record['commonsense']['pass'] / 8000
        result['Commonsense Constraint Macro Pass Rate'] = final_commonsense_cnt / 1000
        result['Hard Constraint Micro Pass Rate'] = constraint_dis_record['hard']['pass'] / 2290
        result['Hard Constraint Macro Pass Rate'] = final_hardConstraint_cnt / 1000
        result['Final Pass Rate'] = final_all_cnt / 1000
    
    detailed_dict = {
        "Commonsense Constraint": remap_commonsense_constraint_record,
        "Hard Constraint": remap_hard_constraint_record
    }
    if return_per_query:
        return result, detailed_dict, per_query_results
    return result, detailed_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--set_type", type=str, default="validation")
    parser.add_argument("--evaluation_file_path", type=str, default="./")
    parser.add_argument("--query_indices", type=str, default=None, help="Range of query indices to evaluate, e.g. 1-55")
    parser.add_argument("--output_json_path", type=str, default=None, help="Path to save evaluation results in JSON format")
    args = parser.parse_args()

    scores, detailed_scores, per_query_results = eval_score(
        args.set_type,
        file_path=args.evaluation_file_path,
        query_indices=args.query_indices,
        return_per_query=True
    )

    print("\n" + "=" * 55)
    print("📈 EVALUATION SUMMARY SCORES")
    print("=" * 55)
    for key in scores:
        print(f"• {key}: {scores[key]*100:.2f}%")

    if not args.query_indices and 0 < scores.get('Delivery Rate', 0) < 1.0:
        delivery_rate = scores['Delivery Rate']
        total_queries = 180 if args.set_type == 'validation' else (1000 if args.set_type == 'test' else 45)
        delivered_queries = round(delivery_rate * total_queries)
        print("\n" + "=" * 55)
        print(f"📊 SUBSET EVALUATION ({delivered_queries}/{total_queries} queries tested)")
        print("=" * 55)
        print(f"Delivery Rate: 100.0% ({delivered_queries}/{delivered_queries})")
        print(f"Subset Commonsense Macro Pass Rate: {scores['Commonsense Constraint Macro Pass Rate'] / delivery_rate * 100:.2f}%")
        print(f"Subset Hard Constraint Macro Pass Rate: {scores['Hard Constraint Macro Pass Rate'] / delivery_rate * 100:.2f}%")
        print(f"Subset Final Pass Rate: {scores['Final Pass Rate'] / delivery_rate * 100:.2f}%")
        print("=" * 55)

    # Save results to JSON file
    output_json_path = args.output_json_path
    if not output_json_path:
        base_name = os.path.splitext(os.path.basename(args.evaluation_file_path))[0]
        eval_dir = os.path.dirname(args.evaluation_file_path)
        output_json_path = os.path.join(eval_dir, f"{base_name}_eval_results.json") if eval_dir else f"./{base_name}_eval_results.json"

    eval_json_data = {
        "set_type": args.set_type,
        "evaluation_file_path": args.evaluation_file_path,
        "query_indices": args.query_indices,
        "summary": {k: f"{v*100:.2f}%" for k, v in scores.items()},
        "metrics": scores,
        "detailed_statistics": detailed_scores,
        "per_query_evaluation": per_query_results
    }

    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_json_path)), exist_ok=True)
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(eval_json_data, f, indent=4, ensure_ascii=False)
        print(f"\n[+] Results saved to JSON: {os.path.abspath(output_json_path)}")
    except Exception as e:
        print(f"\n[-] Failed to save JSON results: {e}")