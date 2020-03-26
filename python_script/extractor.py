
from func import *
from constant import *
import subfields
import os


class ResumeExtractor:

    def __init__(self):
        raw_field_dict = load_json('config/resume_key.json')
        self.sorted_keys = self.sort_field_dict(raw_field_dict)
        self.temp_personal = []

    @staticmethod
    def sort_field_dict(key_dict):
        key_list = []
        for field_key in key_dict.keys():
            for key_ind in range(len(key_dict[field_key])):
                sub_key = key_dict[field_key][key_ind].lower()
                key_list.append([field_key, sub_key, len(sub_key)])

        key_list = sorted(key_list, key=lambda l: l[2], reverse=True)

        return key_list

    @staticmethod
    def get_text(filename):
        """
            Get the text from pdf/doc/docx files
        """
        file_ext = os.path.splitext(filename)[1].lower()[1:]
        if file_ext == 'pdf':
            text_data_raw = get_text_pdf(filename)
        elif file_ext in ['docx', 'doc']:
            text_data_raw = get_text_pdf(filename)
        else:
            text_data_raw = ''

        # remove empty lines
        text_data_lines = text_data_raw.splitlines()
        text_data = ''
        for i in range(len(text_data_lines)):
            if text_data_lines[i] != '' and not text_data_lines[i].startswith('Page ') and \
                    not text_data_lines[i].endswith(' Page'):
                text_data += text_data_lines[i] + '\n'

        # save text as temp
        save_text('a.txt', text_data)

        return text_data

    def get_field_raw(self, text):
        """
            extract the raw field data using config file and return as json
        """
        field_data = {}

        # convert for table
        text_lines_org = text.splitlines()
        new_text = ''
        for line_ind in range(len(text_lines_org)):
            text_line = text_lines_org[line_ind].decode('utf8').strip()
            if text_line != '' and text_line[0] == '|' and text_line[-1] == '|' and text_line.count('|') > 1:
                text_line = text_line[1:-1]
                text_line = text_line.replace('|', '\n')
            elif line_ind < 3:
                text_line = text_line.replace('|', '\n')

            if text_line.replace('_', '') == '':
                continue
            else:
                new_text += text_line + '\n'

        # new_text = new_text.decode("utf-8")

        # replace the text using replace_list dict
        for i in range(len(replace_list_email)):
            new_text = new_text.replace(replace_list_email[i][0], replace_list_email[i][1])
        for i in range(len(replace_list_phone)):
            new_text = new_text.replace(replace_list_phone[i][0], replace_list_phone[i][1])
        for i in range(len(replace_list_key)):
            new_text = new_text.replace(replace_list_key[i][0], replace_list_key[i][1])
        for i in range(len(replace_list)):
            new_text = new_text.replace(replace_list[i][0], replace_list[i][1])

        text_lines = new_text.splitlines()
        # text_lines = new_text.encode("utf-8").splitlines()
        cur_key = 'Header'
        f_personal = False

        for line_ind in range(len(text_lines)):
            text_line = text_lines[line_ind]
            cur_text = text_line

            # pre-processing for key detection
            text_line = text_line.lstrip(".!_o* ").strip()
            text_line = text_line.lstrip(u"\uf0b7").strip()
            text_line = text_line.lstrip(u"\uf0fc").strip()
            text_line = text_line.lstrip(u"\uf0a7").strip()
            text_line = text_line.lstrip(u"\uf076").strip()
            if len(text_line) > 2 and text_line[0].isdigit() and text_line[1] == ' ':
                text_line = text_line[2:]
            text_line = " ".join(text_line.split())

            if text_line == '':
                continue
            elif text_line[0].isupper():
                for key_ind in range(len(self.sorted_keys)):
                    field_key = self.sorted_keys[key_ind][0]
                    sub_key = self.sorted_keys[key_ind][1]

                    if not text_line.lower().startswith(sub_key[:-1]) and \
                            text_line.replace(' ', '').lower() != sub_key.replace(' ', ''):
                        continue
                    elif sub_key == 'responsibilities' and cur_key in ['Work Experience', 'Employment', 'Career']:
                        continue
                    elif sub_key == 'job responsibilities' and cur_key in ['Experience', 'Career']:
                        continue
                    elif sub_key == 'key responsibilities' and cur_key in ['Career']:
                        continue
                    elif sub_key == 'company profile' and cur_key == 'Work Experience':
                        continue
                    elif sub_key == 'achievements' and cur_key == 'Work Experience':
                        continue
                    elif sub_key == 'key competencies' and cur_key == 'Work Experience':
                        continue
                    elif sub_key == 'trainings' and cur_key == 'Work Experience':
                        continue
                    elif sub_key == 'location' and cur_key == 'Qualification':
                        continue
                    elif sub_key == 'key result areas' and cur_key in ['Career', 'Employment']:
                        continue
                    elif sub_key == 'job profile' and cur_key in \
                            ['Work Experience', "Experience", 'Work Profile', 'Employment']:
                        continue
                    elif sub_key == 'objective' and cur_key == 'Professional Reference':
                        continue
                    elif sub_key == 'subject' and cur_key == 'Education':
                        continue
                    elif sub_key == 'company profile' and cur_key == 'Work Profile':
                        continue
                    elif sub_key in ["qualifications", "qualification"] and cur_key == "Education" and \
                            (cur_key not in field_data or len(field_data[cur_key]) < 25):
                        continue
                    elif sub_key in ["name"] and cur_key == "Experience" and \
                            (cur_key not in field_data or len(field_data[cur_key]) < 25):
                        continue
                    elif sub_key in ["organization"] and cur_key == "Internship" and \
                            (cur_key not in field_data or len(field_data[cur_key]) < 25):
                        continue
                    elif sub_key in ["location"] and cur_key == "Employment" and \
                            (cur_key not in field_data or len(field_data[cur_key]) < 25):
                        continue

                    if text_line.lower() == sub_key or \
                            text_line.replace(' ', '').lower() == sub_key.replace(' ', ''):
                        cur_key = field_key
                        cur_text = ''
                        break
                    elif sub_key[-1] == '*':
                        cur_key = field_key
                        cur_text = ''
                        break
                    elif text_line.lower().startswith(sub_key + ':-'):
                        cur_key = field_key
                        cur_text = text_line[len(sub_key) + 2:]
                        break
                    elif text_line.lower().startswith(sub_key + ' :-'):
                        cur_key = field_key
                        cur_text = text_line[len(sub_key) + 3:]
                        break
                    elif text_line.lower().startswith(sub_key + '.'):
                        cur_key = field_key
                        cur_text = text_line[len(sub_key) + 1:]
                        break
                    elif text_line.lower().startswith(sub_key + '________'):
                        cur_key = field_key
                        cur_text = ''
                        break

                    f_check = False
                    for i in range(len(text_line) - len(sub_key)):
                        if text_line.lower().startswith(sub_key + ' ' * i + ':'):
                            cur_key = field_key
                            cur_text = text_line[len(sub_key) + i + 1:]
                            f_check = True
                            break
                    if f_check:
                        break

                    for i in range(len(text_line) - len(sub_key)):
                        if text_line.lower().startswith(sub_key + ' ' * i + '-'):
                            cur_key = field_key
                            cur_text = text_line[len(sub_key) + i + 1:]
                            f_check = True
                            break
                    if f_check:
                        break

                    if text_line.lower().startswith(sub_key) and field_key in ["DOB", "Marital Status"] and \
                            not (text_line[len(sub_key)] == ' ' and text_line[len(sub_key) + 1].islower()):
                        cur_key = field_key
                        cur_text = text_line[len(sub_key):]
                        break

            # Store temp data for "Personal Details"
            if cur_key in ['Declaration', "Achievements", "Skills", "Expertise"]:
                f_personal = False
            if f_personal and cur_key != 'Personal Details' and \
                    (len(self.temp_personal) == 0 or cur_key != self.temp_personal[-1]):
                self.temp_personal.append(cur_key)
            if cur_key == 'Personal Details':
                f_personal = True

            # Update field data
            if cur_key in field_data:
                field_data[cur_key] += ('\n' + cur_text)
            elif cur_text not in ['', ':']:
                field_data[cur_key] = cur_text.strip()

        return field_data

    def fix_field_data(self, field_data):
        """
            Fix the incorrect result from the raw field data and return it
        """
        if "Header" in field_data:
            temp_headers = field_data["Header"].replace('\n', '  ').split('  ')
        else:
            temp_headers = []

        # extract "Name" from the "Header"
        if "Name" not in field_data and "Header" in field_data:
            for i in range(len(temp_headers)):
                if temp_headers[i].lower() in no_name_list:
                    continue
                elif 'department' in temp_headers[i].lower():
                    continue
                elif check_name(temp_headers[i]):
                    field_data["Name"] = temp_headers[i]
                    break
                elif i == 0 and temp_headers[i].count(',') == 1 and check_name(temp_headers[i].split(',')[0]):
                    field_data["Name"] = temp_headers[i].split(',')[0].lstrip('Professional Profile of ')
                    break
                elif i == 0 and temp_headers[i].count('-') == 1 and check_name(temp_headers[i].split('-')[0]):
                    # 'Shivlal Barthare - PMP\xae'
                    field_data["Name"] = temp_headers[i].split('-')[0]

            if "Name" in field_data and len(field_data['Name']) > 30:
                del field_data['Name']

        # extract the "Email" from the "Header"
        if "Email" not in field_data and "Header" in field_data:
            for i in range(len(temp_headers)):
                if check_mail(temp_headers[i]):
                    field_data["Email"] = temp_headers[i]
                    break

        # extract the "Contact Number" from the "Header"
        if "Contact Number" not in field_data and "Header" in field_data:
            for i in range(len(temp_headers)):
                if check_phone(temp_headers[i]):
                    field_data["Contact Number"] = temp_headers[i]
                    break
                elif temp_headers[i].startswith('M :'):
                    field_data["Contact Number"] = temp_headers[i][3:].strip()
                    break

        # extract the "Linkedin" from the "Header"
        if "Linkedin" not in field_data and "Header" in field_data:
            for i in range(len(temp_headers)):
                if check_linkedin(temp_headers[i]):
                    field_data["Linkedin"] = temp_headers[i]
                    break

        # extract "Sex" from "Header"
        if "Sex" not in field_data and "Header" in field_data:
            if "female" in field_data["Header"].lower():
                field_data['Sex'] = 'Female'
            elif "male" in field_data["Header"].lower():
                field_data['Sex'] = 'Female'

        # extract "Martial Status" from "Header"
        if "Marital Status" not in field_data and "Header" in field_data:
            if "unmarried" in field_data["Header"].lower():
                field_data['Marital Status'] = 'Unmarried'
            elif "married" in field_data["Header"].lower():
                field_data['Marital Status'] = 'Married'
            elif "single" in field_data["Header"].lower():
                field_data['Marital Status'] = 'Single'

        # extract "DOB" from the "Contact Number"
        if "Contact Number" in field_data and "DOB" not in field_data:
            temp_data = field_data["Contact Number"].splitlines()
            if len(temp_data) == 2 and check_phone(temp_data[1]) and len(temp_data[0].split()) == 3:
                field_data["DOB"] = temp_data[0]
                field_data["Contact Number"] = temp_data[1]

        # extract "Name" from the "Contact Number"
        if "Contact Number" in field_data and "Name" not in field_data:
            temp_data = field_data["Contact Number"].splitlines()
            if len(temp_data) > 1 and check_phone(temp_data[0]):
                field_data["Contact Number"] = temp_data[0]
                if check_name(temp_data[1]):
                    field_data["Name"] = temp_data[1]
                elif len(temp_data) > 2 and check_phone(temp_data[1]) and check_name(temp_data[2]):
                    field_data["Contact Number"] += ',' + temp_data[1]
                    field_data["Name"] = temp_data[2]

        # extract the "Email" from the "Contact Number"
        if "Contact Number" in field_data and "Email" not in field_data:
            temp_data = field_data["Contact Number"].splitlines()
            if len(temp_data) == 2 and temp_data[1].isdigit() and check_mail(temp_data[0]):
                field_data["Email"] = temp_data[0]
                field_data["Contact Number"] = temp_data[1]
            else:
                if temp_data[0].count(',') == 1:
                    temp_data = temp_data[0].split(',')
                    if check_phone(temp_data[1]) and check_mail(temp_data[0]):
                        field_data["Email"] = temp_data[0]
                        field_data["Contact Number"] = temp_data[1]
                    elif check_phone(temp_data[0]) and check_mail(temp_data[1]):
                        field_data["Email"] = temp_data[1]
                        field_data["Contact Number"] = temp_data[0]
                elif temp_data[0].count(' ') == 1:
                    temp_data = temp_data[0].split(' ')
                    if check_phone(temp_data[1]) and check_mail(temp_data[0]):
                        field_data["Email"] = temp_data[0]
                        field_data["Contact Number"] = temp_data[1]
                    elif check_phone(temp_data[0]) and check_mail(temp_data[1]):
                        field_data["Email"] = temp_data[1]
                        field_data["Contact Number"] = temp_data[0]

        # extract the "Contact No", "Email" from "Address"
        if "Contact Number" not in field_data and "Email" not in field_data and "Address" in field_data:
            temp_data = field_data["Address"].splitlines()
            if len(temp_data) == 3 and check_mail(temp_data[1]) and check_phone(temp_data[0]):
                field_data["Contact Number"] = temp_data[0]
                field_data["Email"] = temp_data[1]
                field_data["Address"] = temp_data[2]
            elif len(temp_data) == 2 and check_mail(temp_data[1]) and check_phone(temp_data[0]):
                # "9833126586\nrlapurva@yahoo.co.in"
                field_data["Contact Number"] = temp_data[0]
                field_data["Email"] = temp_data[1]
                del field_data["Address"]
            else:
                # u'+91 9821253858, shindesudhir2301@gmail.com.\nPage 2 of 2'
                if ',' in temp_data[0] and '@' in temp_data[0]:
                    new_temp = temp_data[0].split(',')
                    if len(temp_data) == 2 and check_mail(new_temp[1]) and check_phone(new_temp[0]):
                        field_data["Contact Number"] = new_temp[0]
                        field_data["Email"] = new_temp[1]
                        field_data['Address'] = '\n'.join(temp_data[1:])

        # extract the "Name" from the "Email"
        if "Email" in field_data and "Name" not in field_data:
            temp_data = field_data["Email"].splitlines()
            if len(temp_data) == 1:
                if ' ' in temp_data[0] and '.com' in temp_data[0] and \
                        temp_data[0].index('.com') < temp_data[0].index(' '):
                    # 'vishu_sawant86@yahoo.comVishal R. Sawant'
                    new_temp_lines = temp_data[0].split('.com')
                    field_data["Email"] = new_temp_lines[0] + '.com'
                    if check_name(new_temp_lines[1]):
                        field_data["Name"] = new_temp_lines[1]
            else:
                for i in range(len(temp_data)):
                    if check_name(temp_data[i]):
                        field_data["Name"] = temp_data[i]
                        break

        # extract the "LinkedIn" from the "Email"
        if "Email" in field_data and "LinkedIn" not in field_data:
            temp_data = field_data["Email"].splitlines()
            for i in range(len(temp_data)):
                if check_linkedin(temp_data[i]):
                    field_data["LinkedIn"] = temp_data[i]
                    break

        # extract the "Martial Status" from the "Sex"
        if "Sex" in field_data and "Martial Status" not in field_data:
            if '&' in field_data["Sex"]:
                temp_data = field_data["Sex"].lstrip(':-\n').split('&')
                for i in range(len(temp_data)):
                    if check_gender(temp_data[i].strip()):
                        field_data["Sex"] = temp_data[i].strip()
                    elif check_marry(temp_data[i].strip()):
                        field_data["Martial Status"] = temp_data[i].strip()

        # extract the "Name" from the "DOB"
        if "DOB" in field_data and "Name" not in field_data:
            temp_data = field_data["DOB"].splitlines()
            for i in range(len(temp_data)):
                if check_name(temp_data[i]):
                    field_data["Name"] = temp_data[i]
                    break

        # extract "Contact Number" from the "Email", ,
        if "Contact Number" not in field_data and "Email" in field_data:
            if '@' in field_data["Email"] and ';' in field_data["Email"]:   # '9654417682 ; bhawnagulati12@gmail.com'
                temp_data = field_data["Email"].split(';')
                for i in range(len(temp_data)):
                    if check_phone(temp_data[i]):
                        field_data["Contact Number"] = temp_data[i]
                    elif check_mail(temp_data[i]):
                        field_data["Email"] = temp_data[i]
            elif '@' in field_data["Email"] and ' I ' in field_data["Email"]:  # 'India I +91-900495 I sa.oj@gmail.com'
                temp_data = field_data["Email"].split(' I ')
                for i in range(len(temp_data)):
                    if check_phone(temp_data[i]):
                        field_data["Contact Number"] = temp_data[i]
                    elif check_mail(temp_data[i]):
                        field_data["Email"] = temp_data[i]
            elif '@' in field_data["Email"] and ' ' in field_data["Email"]:  # '+91-900495 sa.oj@gmail.com'
                temp_data = field_data["Email"].split(' ')
                for i in range(len(temp_data)):
                    if check_phone(temp_data[i]):
                        field_data["Contact Number"] = temp_data[i]
                    elif check_mail(temp_data[i]):
                        field_data["Email"] = temp_data[i]

        # extract "DOB" from the "Sex"
        if "DOB" not in field_data and "Sex" in field_data:
            temp_data = field_data["Sex"].splitlines()
            if len(temp_data) == 2 and check_gender(temp_data[1]) and len(temp_data[0].split()) == 3:
                field_data['DOB'] = temp_data[0]
                field_data['Sex'] = temp_data[1]

        # extract "DOB" from the "Martial Status"
        if "DOB" not in field_data and "Marital Status" in field_data:
            temp_data = field_data["Marital Status"].splitlines()
            if len(temp_data) >= 2 and check_marry(temp_data[1]) and len(temp_data[0].strip('-').split()) == 3:
                field_data['DOB'] = temp_data[0]
                field_data['Marital Status'] = temp_data[1]

        # extract the "Contact Number" from the "Email"
        if "Email" in field_data and "Contact Number" not in field_data:
            temp_data = field_data["Email"].splitlines()
            for i in range(len(temp_data)):
                if check_phone(temp_data[i]):
                    field_data["Contact Number"] = temp_data[i]
                    break

        # extract the "Language" from the "Hobbies"
        if "Hobbies" in field_data and "Languages" not in field_data:
            temp_data = field_data["Hobbies"].splitlines()
            if len(temp_data) == 2 and check_language(temp_data[1]):
                field_data["Hobbies"] = temp_data[0]
                field_data["Languages"] = temp_data[1]

        # extract the "Language" from the "Marital Status"
        if "Marital Status" in field_data and "Languages" not in field_data:
            temp_data = field_data["Marital Status"].splitlines()
            if len(temp_data) == 2 and check_language(temp_data[0]) and check_marry(temp_data[1]):
                field_data["Languages"] = temp_data[0]
                field_data["Marital Status"] = temp_data[1]

        # extract "Email", "linkedin" from the "Contact Number"
        if "Contact Number" in field_data and "Email" not in field_data and "LinekdIn" not in field_data:
            temp_data = field_data["Contact Number"].splitlines()
            for i in range(len(temp_data)):
                if check_phone(temp_data[i]):
                    field_data["Contact Number"] = temp_data[i]
                elif check_mail(temp_data[i]):
                    field_data["Email"] = temp_data[i]
                elif check_linkedin(temp_data[i]):
                    field_data["LinkedIn"] = temp_data[i]

        # extract "Sex" from "Personal Details"
        if "Sex" not in field_data and "Personal Details" in field_data:
            if "female" in field_data["Personal Details"].lower():
                field_data['Sex'] = 'Female'
            elif "male" in field_data["Personal Details"].lower():
                field_data['Sex'] = 'Female'

        # extract "Martial Status" from "Personal Details"
        if "Marital Status" not in field_data and "Personal Details" in field_data:
            if "unmarried" in field_data["Personal Details"].lower():
                field_data['Marital Status'] = 'Unmarried'
            elif "married" in field_data["Personal Details"].lower():
                field_data['Marital Status'] = 'Married'
            elif "single" in field_data["Personal Details"].lower():
                field_data['Marital Status'] = 'Single'

        # for "Personal Details" data
        if len(self.temp_personal) == 1:
            if "Personal Details" in field_data:
                temp_data = field_data["Personal Details"].splitlines()
                for i in range(len(temp_data)):
                    if check_marry(temp_data[i]) and "Marital Status" not in field_data:
                        field_data["Marital Status"] = temp_data[i]
                    elif check_language(temp_data[i]) and "Languages" not in field_data:
                        field_data["Languages"] = temp_data[i]
        elif len(self.temp_personal) > 1:
            if any(s in field_data and s != 'Email' for s in self.temp_personal[1:-1]) or \
                    self.temp_personal[-1] not in field_data:
                pass
            else:
                temp_data = field_data[self.temp_personal[-1]].splitlines()
                if self.temp_personal[-1].count(':') > max(len(self.temp_personal) - 2, 1):
                    f_colon = True
                else:
                    f_colon = False

                temp_data_fields = []
                for i in range(len(temp_data)):
                    if f_colon:
                        if temp_data[i][0] == ':' or i == 0:
                            temp_data_fields.append(temp_data[i])
                        else:
                            temp_data_fields[-1] += '\n' + temp_data[i]
                    else:
                        if temp_data[i] in ['a', ':']:
                            continue
                        elif temp_data[i].startswith('I declare '):
                            break
                        elif temp_data[i].startswith('I hereby '):
                            break
                        else:
                            temp_data_fields.append(temp_data[i])

                if len(self.temp_personal) == len(temp_data_fields):
                    if self.temp_personal[-1] == 'Professional Reference' and self.temp_personal[0] != 'Fathers Name'\
                            and temp_data_fields[0].replace(' ', '').isalpha():
                        for i in range(len(temp_data_fields) - 1):
                            field_data[self.temp_personal[i]] = temp_data_fields[i + 1]
                        field_data[self.temp_personal[len(temp_data_fields) - 1]] = temp_data_fields[0]
                    elif self.temp_personal[-1] == 'Languages' and check_language(temp_data_fields[0]):
                        pass
                    else:
                        for i in range(len(temp_data_fields)):
                            field_data[self.temp_personal[i]] = temp_data_fields[i]
                elif len(self.temp_personal) + 1 == len(temp_data_fields):
                    if temp_data_fields[-1].startswith('Reference'):
                        for i in range(len(self.temp_personal)):
                            field_data[self.temp_personal[i]] = temp_data_fields[i]
                    if len(temp_data_fields[0]) > 2 and temp_data_fields[0][0] + temp_data_fields[0][-1] == '()':
                        for i in range(len(self.temp_personal)):
                            field_data[self.temp_personal[i]] = temp_data_fields[i + 1]
                    else:
                        for i in range(len(self.temp_personal)):
                            field_data[self.temp_personal[i]] = temp_data_fields[i]

        # "Nationality": ": Male\n: Shri Dinesh Kumar Dubey\n: 27/05/1988\n: Married\n: Indian"
        # "Nationality":  ":\n:\n:\n:\n:\n8th May, 1987\nEnglish, Hindi, Gujarati and Marathi\nFemale\nSingle\nIndian"
        if "Nationality" in field_data:
            temp_data = field_data["Nationality"].lstrip(':-\n').splitlines()
            f_check = False

            for i in range(len(temp_data)):
                if temp_data[i][0] == ":":
                    temp_data_line = temp_data[i][1:].strip()
                    temp_data[i] = temp_data_line
                else:
                    temp_data_line = temp_data[i]

                if "Sex" not in field_data and check_gender(temp_data_line.lower()):
                    field_data["Sex"] = temp_data_line
                    f_check = True
                elif "Marital Status" not in field_data and check_marry(temp_data_line):
                    field_data["Marital Status"] = temp_data_line
                    f_check = True
                elif "Languages" not in field_data and check_language(temp_data_line):
                    field_data["Languages"] = temp_data_line
                    f_check = True
                elif "DOB" not in field_data and (temp_data_line.count('/') == 2 or len(temp_data_line.split()) == 3):
                    field_data["DOB"] = temp_data_line
                    f_check = True

            if f_check:
                field_data["Nationality"] = temp_data[-1]
            else:
                if temp_data[0].startswith("Preferred work") and len(temp_data) > 1:
                    field_data["Nationality"] = temp_data[1]
                else:
                    field_data["Nationality"] = temp_data[0]

        # "Fathers Name": "4TH March 1984\n Shrawan..."
        if "DOB" not in field_data and "Fathers Name" in field_data:
            temp_data = field_data["Fathers Name"].splitlines()
            for i in range(len(temp_data)):
                f_digit = False
                for j in range(len(temp_data[i])):
                    if temp_data[i][j].isdigit():
                        f_digit = True
                        break

                if f_digit:
                    field_data["DOB"] = temp_data[i]
                else:
                    field_data["Fathers Name"] = temp_data[i]

        # clean "DOB":  'th\n: 13 October 1990'
        if "DOB" in field_data:
            field_data["DOB"] = field_data["DOB"].lstrip('th\n')

        # clean "Contact Number": 'Professional \n\n 9710...'
        if "Contact Number" in field_data:
            temp_data = field_data["Contact Number"].splitlines()
            for i in range(len(temp_data)):
                if check_phone(temp_data[i]):
                    field_data["Contact Number"] = temp_data[i]
                    break

        # clean "Email" and extract more fields
        if "Email" in field_data:
            temp_data = field_data["Email"].replace(',', '\n').replace(';', '\n').splitlines()
            temp_mail = []
            temp_phone = []
            for i in range(len(temp_data)):
                if check_mail(temp_data[i]):
                    if temp_data[i].strip() not in temp_mail:
                        temp_mail.append(temp_data[i].strip())
                if check_phone(temp_data[i].strip()):
                    if temp_data[i] not in temp_phone:
                        temp_phone.append(temp_data[i].strip())

            if len(temp_mail) == 0:
                del field_data["Email"]
            else:
                field_data["Email"] = ','.join(temp_mail)

            if 'Contact Number' not in field_data and len(temp_phone) > 0:
                field_data["Contact Number"] = ','.join(temp_phone)

        # get first line from the below fields
        for field in ["Age", "LinkedIn", "Email", "DOB", "Sex", "Contact Number", "Skype", "Fathers Name", "Marital Status"]:
            if field in field_data:
                if field_data[field].startswith(':\n') or field_data[field].startswith('-\n'):
                    field_data[field] = field_data[field][2:]
                elif field_data[field].startswith(':-\n'):
                    field_data[field] = field_data[field][3:]
                field_data[field] = field_data[field].splitlines()[0]

        # get first line if "Address" is too long
        if "Address" in field_data:
            if len(field_data["Address"]) > 100:
                field_data["Address"] = field_data["Address"].splitlines()[0]

        # clean fields
        empty_field = []
        for field in field_data:
            field_data[field] = field_data[field].strip("|:-~ ")
            if field_data[field] == '' or field_data[field].startswith('Page ') and \
                    len(field_data[field].splitlines()) == 1:
                empty_field.append(field)

        for field in empty_field:
            del field_data[field]

        return field_data

    def extract(self, filename):
        # --------------------- Get full text from the file -------------------
        data_text = self.get_text(filename)

        # ------------------ extract the data using raw_extractor -------------
        data_field_raw = self.get_field_raw(data_text)

        # ---------------------- fix the incorrect results --------------------
        data_field_fix = self.fix_field_data(data_field_raw)

        # -------------------------- extract subfields ------------------------
        data_final = subfields.extract_subfields(data_field_fix)

        return data_final


if __name__ == '__main__':
    pass
