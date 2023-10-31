#!/usr/bin/python3
import fire

def main(in_path, out_path="./output"):
    print(f"Reading {in_path}, Writing to {out_path}")

if __name__ == '__main__':
    fire.Fire(main)
