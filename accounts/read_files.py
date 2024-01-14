import os

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def write_to_file(output_file, content):
    with open(output_file, 'a', encoding='utf-8') as file:
        file.write(content)

def process_python_file(file_path, output_file):
    content = read_file(file_path)
    write_to_file(output_file, f"\n\n{'='*20} {file_path} {'='*20}\n{content}\n{'='*50}\n\n")

def process_templates_folder(templates_folder, output_file):
    for root, dirs, files in os.walk(templates_folder):
        for file in files:
            file_path = os.path.join(root, file)
            content = read_file(file_path)
            write_to_file(output_file, f"\n\n{'='*20} {file_path} {'='*20}\n{content}\n{'='*50}\n\n")

if __name__ == "__main__":
    output_file_path = "output.txt"

    # Process individual Python files
    python_files = ['urls.py', 'views.py', 'models.py', 'forms.py']
    for python_file in python_files:
        process_python_file(python_file, output_file_path)

    # Process files in the templates folder
    templates_folder_path = "templates"
    process_templates_folder(templates_folder_path, output_file_path)

    print(f"Data has been written to {output_file_path}.")
