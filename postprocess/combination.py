import os
import json
import argparse
from tqdm import tqdm
from datasets import load_dataset


def parse_query_indices(query_indices, max_len=None):
    if not query_indices:
        return None
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
    return set(indices)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--set_type", type=str, default="validation")
    parser.add_argument("--model_name", type=str, default="gpt-3.5-turbo-1106")
    parser.add_argument("--query_indices", type=str, default=None, help="Range of query indices to include, e.g. 1-55")
    parser.add_argument("--mode", type=str, default="two-stage")
    parser.add_argument("--strategy", type=str, default="direct")
    parser.add_argument("--output_dir", type=str, default="./")
    parser.add_argument("--submission_file_dir", type=str, default="./")

    args = parser.parse_args()

    if args.mode == 'two-stage':
        suffix = ''
    elif args.mode == 'sole-planning':
        suffix = f'_{args.strategy}'

    if args.set_type == 'train':
        query_data_list  = load_dataset('osunlp/TravelPlanner','train')['train']
    elif args.set_type == 'validation':
        query_data_list  = load_dataset('osunlp/TravelPlanner','validation')['validation']
    elif args.set_type == 'test':
        query_data_list  = load_dataset('osunlp/TravelPlanner','test')['test']

    allowed_set = parse_query_indices(args.query_indices, len(query_data_list))
    idx_number_list = [i for i in range(1, len(query_data_list)+1)]
    submission_list = []
    valid_plans_count = 0

    for idx in tqdm(idx_number_list, desc="Combining plans"):
        if allowed_set is not None and idx not in allowed_set:
            submission_list.append({"idx": idx, "query": query_data_list[idx-1]['query'], "plan": None})
            continue

        plan_file = f'{args.output_dir}/{args.set_type}/generated_plan_{idx}.json'
        plan = None
        if os.path.exists(plan_file):
            try:
                generated_plan = json.load(open(plan_file, encoding='utf-8'))
                plan = generated_plan[-1].get(f'{args.model_name}{suffix}_{args.mode}_parsed_results', None)
                if plan is not None:
                    valid_plans_count += 1
            except Exception:
                plan = None
        submission_list.append({"idx": idx, "query": query_data_list[idx-1]['query'], "plan": plan})
    
    clean_model_name = args.model_name.replace('/', '_')
    os.makedirs(args.submission_file_dir, exist_ok=True)
    out_path = f'{args.submission_file_dir}/{args.set_type}_{clean_model_name}{suffix}_{args.mode}_submission.jsonl'
    
    with open(out_path, 'w', encoding='utf-8') as w:
        for unit in submission_list:
            output = json.dumps(unit)
            w.write(output + "\n")
            
    print(f"\nSaved submission to: {out_path}")
    print(f"Total entries: {len(submission_list)} | Non-null parsed plans included: {valid_plans_count}")
