import json
import os

def read_data_from_file(file_path):
    """从JSON文件读取数据"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件 {file_path} 不存在")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    return data

def transform_data_to_dialogue(data):
    """将JSON数据转换为对话格式
    格式: |销售：哪个那边不能|专家：|"""
    # 提取转录数据和身份识别数据
    transcription_data = data["transaction"]["Transcription"]
    identity_data = data["introspection"]["IdentityRecognition"]
    
    # 获取身份识别映射
    identity_map = {}
    for identity in identity_data["IdentityResults"]:
        identity_map[identity["SpeakerId"]] = identity["Identity"]
    
    # 处理段落数据
    dialogue_lines = []
    
    for paragraph in transcription_data["Paragraphs"]:
        speaker_id = paragraph["SpeakerId"]
        speaker_role = identity_map.get(speaker_id, f"未知{speaker_id}")
        
        # 提取该段落的所有文本
        paragraph_text = "".join([word["Text"] for word in paragraph["Words"]])
        
        # 添加到对话行
        dialogue_lines.append(f"|{speaker_role}：{paragraph_text}")
    
    # 组合所有对话行，并在末尾添加|专家：|
    result = "".join(dialogue_lines) + "|专家：|"
    
    return result

def process_single_file(file_path):
    """处理单个文件"""
    try:
        # 读取数据
        data = read_data_from_file(file_path)
        
        # 转换格式
        dialogue_format = transform_data_to_dialogue(data)
        
        return dialogue_format
        
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return None

def process_multiple_files(file_paths):
    """处理多个文件"""
    results = {}
    
    for file_path in file_paths:
        result = process_single_file(file_path)
        if result:
            results[file_path
] = result
    
    return results

def save_results_to_file(results, output_file):
    """将结果保存到文件"""
    with open(output_file, 'w', encoding='utf-8') as file:
        if isinstance(results, dict):
            for file_path, dialogue in results.items():
                file.write(f"文件: {file_path}\n")
                file.write(f"对话格式: {dialogue}\n")
                file.write("-" * 50 + "\n")
        else:
            file.write(f"对话格式: {results}\n")

def main():
    """主函数"""
    # 方式1: 处理单个文件
    input_file = "input_data.json"  # 替换为您的文件路径
    output_file = "output_result.txt"
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"输入文件 {input_file} 不存在，请创建示例文件...")
        create_sample_file(input_file)
    
    # 处理文件
    result = process_single_file(input_file)
    
    if result:
        print("转换结果:")
        print(result)
        
        # 保存结果到文件
        save_results_to_file(result, output_file)
        print(f"\n结果已保存到: {output_file}")