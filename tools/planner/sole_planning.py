import os
import re
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, "../.."))
sys.path.insert(0, repo_root)
sys.path.insert(0, script_dir)

from agents.prompts import (
    planner_agent_prompt,
    cot_planner_agent_prompt,
    react_planner_agent_prompt,
    react_reflect_planner_agent_prompt,
    reflect_prompt,
)
import json
import time
from langchain_community.callbacks import get_openai_callback

from tqdm import tqdm
from tools.planner.apis import Planner, ReactPlanner, ReactReflectPlanner
import openai
import argparse
from datasets import load_dataset


def parse_query_indices(query_indices, max_len=None):
    if not query_indices:
        return None
    indices = set()
    for part in query_indices.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start, end = part.split('-')
            indices.update(range(int(start), int(end) + 1))
        else:
            indices.add(int(part))
    sorted_indices = sorted(list(indices))
    if max_len is not None:
        sorted_indices = [i for i in sorted_indices if 1 <= i <= max_len]
    return sorted_indices


def load_line_json_data(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.read().strip().split('\n'):
            unit = json.loads(line)
            data.append(unit)
    return data


def extract_numbers_from_filenames(directory):
    pattern = r'annotation_(\d+).json'
    files = os.listdir(directory)
    numbers = [int(re.search(pattern, file).group(1)) for file in files if re.match(pattern, file)]
    return numbers


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--set_type", type=str, default="validation")
    parser.add_argument("--model_name", type=str, default="gpt-3.5-turbo-1106")
    parser.add_argument("--output_dir", type=str, default="./")
    parser.add_argument("--strategy", type=str, default="direct", choices=["direct", "cot", "react", "reflexion"])
    parser.add_argument("--query_indices", type=str, default=None, help="Query indices (e.g. '1-10,15,20-25')")
    args = parser.parse_args()

    # Normalize output_dir to absolute path so execution location does not matter
    args.output_dir = os.path.abspath(args.output_dir)

    if args.set_type == 'train':
        query_data_list = load_dataset('osunlp/TravelPlanner', 'train')['train']
    elif args.set_type == 'validation':
        query_data_list = load_dataset('osunlp/TravelPlanner', 'validation')['validation']
    elif args.set_type == 'test':
        query_data_list = load_dataset('osunlp/TravelPlanner', 'test')['test']
    else:
        raise ValueError(f"Unknown set_type: {args.set_type}")

    if args.query_indices:
        numbers = parse_query_indices(args.query_indices, len(query_data_list))
    else:
        numbers = [i for i in range(1, len(query_data_list) + 1)]

    if args.strategy == 'direct':
        planner = Planner(model_name=args.model_name, agent_prompt=planner_agent_prompt)
    elif args.strategy == 'cot':
        planner = Planner(model_name=args.model_name, agent_prompt=cot_planner_agent_prompt)
    elif args.strategy == 'react':
        planner = ReactPlanner(model_name=args.model_name, agent_prompt=react_planner_agent_prompt)
    elif args.strategy == 'reflexion':
        planner = ReactReflectPlanner(
            model_name=args.model_name,
            agent_prompt=react_reflect_planner_agent_prompt,
            reflect_prompt=reflect_prompt,
        )

    target_dir = os.path.join(args.output_dir, args.set_type)
    os.makedirs(target_dir, exist_ok=True)

    result_key = f'{args.model_name}_{args.strategy}_sole-planning_results'
    logs_key = f'{args.model_name}_{args.strategy}_sole-planning_results_logs'

    with get_openai_callback() as cb:
        for number in tqdm(numbers):
            plan_file = os.path.join(target_dir, f'generated_plan_{number}.json')

            # Resume check: skip if query already has non-empty result
            if os.path.exists(plan_file):
                try:
                    with open(plan_file, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                    if existing and existing[-1].get(result_key) and existing[-1][result_key] != "":
                        print(f"Skipping query {number} (already generated)...")
                        continue
                except Exception:
                    pass

            query_data = query_data_list[number - 1]
            reference_information = query_data['reference_information']

            planner_results = None
            scratchpad = ""
            retry_count = 0
            max_retries = 3

            while retry_count < max_retries:
                try:
                    if args.strategy in ['react', 'reflexion']:
                        planner_results, scratchpad = planner.run(reference_information, query_data['query'])
                    else:
                        planner_results = planner.run(reference_information, query_data['query'])
                    if planner_results is not None:
                        break
                except Exception as e:
                    retry_count += 1
                    print(f"\n[Query {number}] Encountered error: {e}. Retry {retry_count}/{max_retries}...")
                    time.sleep(5)

            if planner_results is None:
                planner_results = ""
                scratchpad = "Execution failed after maximum retries."

            if not os.path.exists(plan_file):
                result = [{}]
            else:
                try:
                    with open(plan_file, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                except Exception:
                    result = [{}]

            if args.strategy in ['react', 'reflexion']:
                result[-1][logs_key] = scratchpad
            result[-1][result_key] = planner_results

            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

        print("\nAPI Usage Summary:")
        print(cb)
