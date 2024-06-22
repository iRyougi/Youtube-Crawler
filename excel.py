import pandas as pd
import re
from collections import Counter

def calculate_lexical_diversity(comment):
    words = re.findall(r'\w+', comment.lower())
    unique_words = set(words)
    if len(words) == 0:
        return 0
    return len(unique_words) / len(words)

def calculate_ttr(comment):
    words = re.findall(r'\w+', comment.lower())
    unique_words = set(words)
    if len(words) == 0:
        return 0
    return len(unique_words) / len(words)

def calculate_average_sentence_length(comment):
    sentences = re.split(r'[.!?]', comment)
    words = re.findall(r'\w+', comment)
    if len(sentences) == 0 or len(words) == 0:
        return 0
    return len(words) / len(sentences)

def is_meaningful(comment):
    # 定义无意义评论的正则表达式
    meaningless_pattern = r'^[\W_]+$'
    return not re.match(meaningless_pattern, comment)

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    video_details = {}
    comments = []
    current_comment = {}

    for line in lines:
        line = line.strip()
        if line.startswith('视频标题:'):
            video_details['title'] = line.split(':', 1)[1].strip()
        elif line.startswith('链接:'):
            video_details['link'] = line.split(':', 1)[1].strip()
        elif line.startswith('播放量:'):
            video_details['views'] = line.split(':', 1)[1].strip()
        elif line.startswith('点赞数:'):
            if current_comment and 'likes' in current_comment and 'comment' in current_comment:
                comments.append(current_comment)
            current_comment = {'likes': int(line.split(':', 1)[1].strip()), 'comment': ''}
        elif line.startswith('评论:'):
            if 'comment' in current_comment:
                current_comment['comment'] += ' ' + line.split(':', 1)[1].strip()
            else:
                current_comment['comment'] = line.split(':', 1)[1].strip()
    
    if current_comment and 'likes' in current_comment and 'comment' in current_comment:
        comments.append(current_comment)

    processed_comments = []
    for comment in comments:
        if 'likes' in comment and 'comment' in comment:
            if is_meaningful(comment['comment']):
                lexical_diversity = calculate_lexical_diversity(comment['comment'])
                ttr = calculate_ttr(comment['comment'])
                avg_sentence_length = calculate_average_sentence_length(comment['comment'])
                processed_comments.append({
                    'Likes': comment['likes'],
                    'Comment': comment['comment'],
                    'Lexical Diversity': lexical_diversity,
                    'Type-Token Ratio (TTR)': ttr,
                    'Average Sentence Length': avg_sentence_length
                })

    df = pd.DataFrame(processed_comments)
    return df

def write_to_excel(df, output_file):
    df.to_excel(output_file, index=False)

# 示例使用
file_path = 'youtube_comments.txt'
output_file = 'output_comments.xlsx'

df = process_file(file_path)
write_to_excel(df, output_file)

print(f"数据已写入 {output_file}")
