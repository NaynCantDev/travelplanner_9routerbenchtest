import os
import argparse
from datasets import load_dataset
from tqdm import tqdm
import json


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


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--set_type", type=str, default="validation")
    parser.add_argument("--model_name", type=str, default="gpt-3.5-turbo-1106")
    parser.add_argument("--query_indices", type=str, default=None, help="Range of query indices to extract, e.g. 1-55")
    parser.add_argument("--mode", type=str, default="two-stage")
    parser.add_argument("--strategy", type=str, default="direct")
    parser.add_argument("--output_dir", type=str, default="./")
    parser.add_argument("--tmp_dir", type=str, default="./")

    args = parser.parse_args()

    if args.mode == 'two-stage':
        suffix = ''
    elif args.mode == 'sole-planning':
        suffix = f'_{args.strategy}'

    clean_model_name = args.model_name.replace('/', '_')
    tmp_path = f'{args.tmp_dir}/{args.set_type}_{clean_model_name}{suffix}_{args.mode}.txt'
    if not os.path.exists(tmp_path):
        legacy_path = f'{args.tmp_dir}/{args.set_type}_{args.model_name}{suffix}_{args.mode}.txt'
        if os.path.exists(legacy_path):
            tmp_path = legacy_path
        else:
            raise FileNotFoundError(
                f"\n[!] Chua tim thay file ket qua parse: '{tmp_path}'\n"
                f"[!] Ly do: Buoc 'parsing.py' chua duoc chay hoac chua tao duoc file ket qua.\n"
                f"[!] Vui long chay 'python parsing.py ...' truoc khi chay 'element_extraction.py'."
            )
        
    results_raw = open(tmp_path, 'r', encoding='utf-8').read().strip().split('\n')
    parsed_dict = {}
    for line in results_raw:
        if not line.strip():
            continue
        parts = line.split('\t', 1)
        if len(parts) >= 2:
            try:
                line_idx = int(parts[0])
                parsed_dict[line_idx] = parts[1]
            except ValueError:
                pass
    
    if args.set_type == 'train':
        query_data_list  = load_dataset('osunlp/TravelPlanner','train')['train']
    elif args.set_type == 'validation':
        query_data_list  = load_dataset('osunlp/TravelPlanner','validation')['validation']
    elif args.set_type == 'test':
        query_data_list  = load_dataset('osunlp/TravelPlanner','test')['test']

    if args.query_indices:
        idx_number_list = parse_query_indices(args.query_indices, len(query_data_list))
    else:
        idx_number_list = [i for i in range(1, len(query_data_list)+1)]

    extracted_count = 0
    for idx in tqdm(idx_number_list, desc="Extracting JSON elements"):
        plan_file = f'{args.output_dir}/{args.set_type}/generated_plan_{idx}.json'
        if not os.path.exists(plan_file):
            continue

        try:
            generated_plan = json.load(open(plan_file, encoding='utf-8'))
        except Exception:
            continue

        plan_raw = generated_plan[-1].get(f'{args.model_name}{suffix}_{args.mode}_results', "")
        if plan_raw not in ["", "Max Token Length Exceeded.", None]:
            result = None
            raw_text = parsed_dict.get(idx)
            if raw_text is None and (idx - 1) < len(results_raw):
                raw_text = results_raw[idx - 1]

            if raw_text:
                if '```json' in raw_text:
                    try:
                        result = raw_text.split('```json')[1].split('```')[0].strip()
                    except Exception:
                        result = None
                elif '```' in raw_text:
                    try:
                        result = raw_text.split('```')[1].split('```')[0].strip()
                    except Exception:
                        result = None
                else:
                    result = raw_text.strip()

            parsed = None
            if result:
                try:
                    parsed = json.loads(result)
                except Exception:
                    try:
                        parsed = eval(result)
                    except Exception:
                        parsed = None

            generated_plan[-1][f'{args.model_name}{suffix}_{args.mode}_parsed_results'] = parsed
            if parsed is not None:
                extracted_count += 1
        else:
            generated_plan[-1][f'{args.model_name}{suffix}_{args.mode}_parsed_results'] = None
  
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(generated_plan, f, indent=4)

    print(f"\nExtracted JSON elements for {extracted_count} plans successfully!")
