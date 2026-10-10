import os
import argparse
from tqdm import tqdm
from openai_request import build_plan_format_conversion_prompt, prompt_chatgpt


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--set_type", type=str, default="validation")
    parser.add_argument("--model_name", type=str, default="gpt-3.5-turbo-1106")
    parser.add_argument("--parser_model_name", type=str, default=None, help="Model used for parsing markdown to JSON (defaults to model_name)")
    parser.add_argument("--query_indices", type=str, default=None, help="Range of query indices to parse, e.g. 1-55, 1,2,3 or 56-180")
    parser.add_argument("--output_dir", type=str, default="../agents/output")
    parser.add_argument("--tmp_dir", type=str, default="./tmp")
    parser.add_argument("--strategy", type=str, default="direct")
    parser.add_argument("--mode", type=str, default="two-stage")
    
    args = parser.parse_args()
    
    if args.mode == 'two-stage':
        suffix = ''
    elif args.mode == 'sole-planning':
        suffix = f'_{args.strategy}'
        
    parser_model = args.parser_model_name if args.parser_model_name else args.model_name
    
    data = build_plan_format_conversion_prompt(
        directory=args.output_dir,
        set_type=args.set_type,
        model_name=args.model_name,
        strategy=args.strategy,
        mode=args.mode,
        query_indices=args.query_indices
    )
    
    clean_model_name = args.model_name.replace('/', '_')
    os.makedirs(args.tmp_dir, exist_ok=True)
    output_file = f'{args.tmp_dir}/{args.set_type}_{clean_model_name}{suffix}_{args.mode}.txt'

    # Track already parsed queries in output_file to avoid re-parsing
    already_parsed_indices = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    idx_str = line.split('\t')[0]
                    try:
                        already_parsed_indices.add(int(idx_str))
                    except ValueError:
                        pass

    total_price = 0
    parsed_count = 0
    skipped_count = 0
    missing_count = sum(1 for _, p in data if not p)
    if missing_count > 0:
        print(f"⚠️  Warning: {missing_count}/{len(data)} queries have no plan file or empty results in {args.output_dir}/{args.set_type}/")
    if missing_count == len(data):
        print("❌ No valid plan files found. Did you run tool_agents.py first?")
    
    for query_idx, prompt in tqdm(data, desc=f"Parsing with {parser_model}"):
        if not prompt:
            continue
        if query_idx in already_parsed_indices:
            skipped_count += 1
            continue
            
        results, _, price = prompt_chatgpt(
            "You are a helpful assistant.",
            index=query_idx,
            save_path=output_file,
            user_input=prompt,
            model_name=parser_model,
            temperature=0
        )
        already_parsed_indices.add(query_idx)
        total_price += price
        parsed_count += 1
        
    print(f"\nDone! Parsed: {parsed_count} queries | Skipped (already done): {skipped_count} | Parsing Cost: ${total_price:.4f}")
    print(f"Results saved to: {output_file}")
