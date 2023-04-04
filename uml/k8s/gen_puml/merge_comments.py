import os
import argparse

PWD = os.path.dirname(os.path.abspath(__file__))


def merge_comment_lines(lines):
    """
    合并连续的多行注释到一行
    """
    merged_lines = []
    comment_lines = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('//'):
            comment_lines.append(stripped_line.lstrip('/').strip())
        else:
            if len(comment_lines) > 0:
                merged_comment = '// ' + ' '.join(comment_lines) + '\n'
                merged_lines.append(merged_comment)
                comment_lines = []
            merged_lines.append(line)
    if len(comment_lines) > 0:
        merged_comment = '// ' + ' '.join(comment_lines) + '\n'
        merged_lines.append(merged_comment)
    return merged_lines


def main():
    parser = argparse.ArgumentParser(description='将 Go 文件中的连续 // 注释合并成一行')
    parser.add_argument('file', metavar='file_name', type=str,
                        help='要处理的 Go 文件名')
    args = parser.parse_args()

    # 读取文件内容
    with open(args.file, 'r') as f:
        lines = f.readlines()

    # 合并多行注释
    merged_lines = merge_comment_lines(lines)
    # print(''.join(merged_lines))
    # 将合并后的内容写回文件
    with open(os.path.join(PWD, 'test.go'), 'w') as f:
        f.writelines(merged_lines)


if __name__ == '__main__':
    main()
