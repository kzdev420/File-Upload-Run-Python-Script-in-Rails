
import textract
import json
import os


def load_text(filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as file1:
            text = file1.read()
    else:
        text = ''

    return text


def save_text(filename, data):
    with open(filename, 'w') as out_file:
        out_file.write(data)


def load_json(filename):
    with open(filename, 'r') as json_file:
        data = json.loads(json_file.read())

    return data


def rm_file(file_name):
    if os.path.isfile(file_name):
        os.remove(file_name)


def get_file_list(root_dir):
    """
        Get all files in root_dir directory
    """
    path_list = []
    file_list = []
    join_list = []

    for path, _, files in os.walk(root_dir):
        for name in files:
            path_list.append(path)
            file_list.append(name)
            join_list.append(os.path.join(path, name))

    return path_list, file_list, join_list


def get_text_pdf(filename):
    """
        Get only text from text-type pdf file
    """
    try:
        pdf_text = textract.process(filename)
    except:
        print("Convert error!")
        import sys
        sys.exit(0)

    return pdf_text


def check_phone(data):
    new_data = data.lstrip(':').replace(';', '').replace('+', '').replace('-', '').replace('/', '').\
        replace('(', '').replace(')', '').replace(' ', '')
    return len(new_data) > 7 and new_data.isdigit()


def check_name(data):
    new_data = data.rstrip(',').replace('.', '').replace("'", '').replace("(", '').replace(")", '').replace(' ', '')
    if new_data == '':
        return False
    elif new_data[0].isupper() and new_data.isalpha():
        return True
    else:
        return False


def check_marry(data):
    return data.strip('-').strip().lower() in ["married", "single", "unmarried"]


def check_language(data):
    return any(s in data.lower() for s in ["english", "hindi"])


def check_linkedin(data):
    if "linkedin.com" in data.lower():
        return True
    else:
        return False


def check_mail(data):
    if '@' in data and '.' in data:
        return True
    else:
        return False


def check_gender(data):
    if data.lower() in ['male', 'female']:
        return True
    else:
        return False
