
import json
from constant import *


def update_name(data):
    if 'Name' in data:
        data_name = data['Name'].split()
        return {'First Name': data_name[0], 'Last Name': ' '.join(data_name[1:])}
    else:
        return {}


def update_address(data):
    def sub_address(address):
        ret_city = ''
        ret_state = ''
        ret_code = ''

        address = address.replace('-', ',')
        temp_list = address.split(',')
        for i in range(len(temp_list)):
            temp_list[i] = temp_list[i].strip('. \n')

        temp_list_last = temp_list[-1].split()

        if len(temp_list) >= 5 and temp_list[-3].isdigit() and temp_list[-2].isalpha() and temp_list[-1].isalpha():
            # Andheri East, Mumbai-400059, Maharashtra, India.')
            ret_state = temp_list[-2]
            ret_city = temp_list[-4]
            ret_code = temp_list[-3]
        elif len(temp_list) >= 3:
            if temp_list[-1].replace(' ', '').isdigit():
                ret_state = temp_list[-3]
                ret_city = temp_list[-2]
                ret_code = temp_list[-1].replace(' ', '')
            elif temp_list[-1].replace(' ', '').isalpha():
                ret_state = temp_list[-2]
                ret_city = temp_list[-1]
            elif len(temp_list_last) > 2 and temp_list_last[-1].isdigit() and temp_list_last[-2].isdigit():
                    ret_state = temp_list[-2]
                    ret_city = ' '.join(temp_list_last[:-2])
                    ret_code = temp_list_last[-2] + temp_list_last[-1]
            elif len(temp_list_last) > 1 and temp_list_last[-1].isdigit():
                    ret_state = temp_list[-2]
                    ret_city = ' '.join(temp_list_last[:-1])
                    ret_code = temp_list_last[-1]
        elif len(temp_list) == 2:
            if temp_list[-1].replace(' ', '').isdigit():
                ret_city = temp_list[-2]
                ret_code = temp_list[-1].replace(' ', '')
            elif temp_list[-1].replace(' ', '').isalpha():
                ret_state = temp_list[-2]
                ret_city = temp_list[-1]
            elif len(temp_list_last) > 2 and temp_list_last[-1].isdigit() and temp_list_last[-2].isdigit():
                    ret_state = temp_list[-2]
                    ret_city = ' '.join(temp_list_last[:-2])
                    ret_code = temp_list_last[-2] + temp_list_last[-1]
            elif len(temp_list_last) > 1 and temp_list_last[-1].isdigit():
                    ret_state = temp_list[-2]
                    ret_city = ' '.join(temp_list_last[:-1])
                    ret_code = temp_list_last[-1]
        elif len(temp_list) == 1:
            ret_city = temp_list[0]

        return ret_city, ret_state, ret_code

    ret = {}
    if 'Address' in data:
        ret_address = sub_address(data['Address'])
        ret['Correspondence City'] = ret_address[0].strip('- ')
        ret['Correspondence State'] = ret_address[1].strip('- ')
        ret['Correspondence Pincode'] = ret_address[2]

    if 'Address_Permanent' in data:
        ret_address = sub_address(data['Address_Permanent'])
        ret['Permanent City'] = ret_address[0].strip('- ')
        ret['Permanent State'] = ret_address[1].strip('- ')
        ret['Permanent Pincode'] = ret_address[2]

    return ret


def update_education(data):
    def check_year(text):
        text = text.strip()
        temp_list = text.replace('.', ' ').replace(')', ' ').split()
        for i in range(len(temp_list)):
            if len(temp_list[i]) == 4 and temp_list[i].isdigit() and temp_list[i][:2] in ['19', '20']:
                return True

        # Aug'12
        if len(text) == 6 and text[:3].lower() in month_short_list and text[4:].isdigit():
            return True

        return False

    def check_mark(text):
        new_text = text.replace('%', ' %').replace('.', '').replace('(', ' ').replace(')', ' ').split()
        if '%' in new_text:
            if new_text[new_text.index('%') - 1].isdigit():
                return True
            else:
                return False
        elif text == 'B+':
            return True
        else:
            return False

    def fix_dict(edu_dict):
        # -------------------------- Marks --------------------------
        if edu_dict['Marks'] != '':
            text = edu_dict['Marks'].replace('%', ' %').replace(')', '').replace('(', ' ').split()
            if '%' in text:
                edu_dict['Marks'] = text[text.index('%') - 1] + '%'

        # --------------------------- Year --------------------------
        if edu_dict['Year'] == '':
            pass
        else:
            temp_list = edu_dict['Year'].replace(')', ' ').split()
            for i in range(len(temp_list)):
                if len(temp_list[i]) == 4 and temp_list[i].isdigit() and temp_list[i][:2] in ['19', '20']:
                    if i > 0 and temp_list[i - 1].lower() not in ['in', 'year']:
                        edu_dict['Year'] = temp_list[i - 1] + ' ' + temp_list[i]
                    else:
                        edu_dict['Year'] = temp_list[i]
                    break

        # ---------------------- University/College -----------------
        str_univ = edu_dict['University'] if 'University' in edu_dict else ''
        str_univ_low = str_univ.lower()
        if 0 < str_univ_low.find('from') < str_univ_low.find('with') < str_univ_low.find('year'):
            # Bachelor of Arts in Political Science from Mumbai University with Second Class - year 1999
            edu_dict['Degree'] = str_univ[:str_univ.find('from')].strip()
            edu_dict['University'] = str_univ[str_univ.find('from') + 4:str_univ.find('with')].strip()
            edu_dict['Year'] = str_univ[str_univ.find('year') + 4:].strip()
        elif 0 < str_univ_low.find('from'):     # "MBA (HR) from VIT University"
            temp = str_univ[:str_univ.find('from')].strip()
            if temp.lower().startswith('post graduate '):
                edu_dict['Graduation'] = 'Post Graduate'
                edu_dict['Degree'] = temp[14:]
            elif temp.lower().startswith('graduate in '):
                edu_dict['Graduation'] = 'Graduate'
                edu_dict['Degree'] = temp[12:]
            elif 'in the year' in temp.lower():
                edu_dict['Degree'] = temp[:temp.lower().find('in the year')].strip()
                edu_dict['Year'] = temp.lower().split('in the year')[1].strip()
            elif edu_dict['Degree'] == '':
                edu_dict['Degree'] = temp

            temp = str_univ[str_univ.find('from') + 4:].strip()
            last_word = temp.replace('(', ' ').replace(')', ' ').split()[-1]
            if ' in ' in temp:
                edu_dict['University'] = temp.split(' in ')[0]
                edu_dict['Year'] = temp.split(' in ')[1]
            elif 0 < temp.lower().find('college') < temp.find('(') and last_word.isdigit() and len(last_word) == 4:
                edu_dict['University'] = temp[:temp.find('(')].strip()
                edu_dict['Year'] = last_word
            else:
                edu_dict['University'] = temp
        elif 0 < str_univ_low.find(' at '):
            # "Attended Summer Internship Programme at University of Cologne"
            edu_dict['Degree'] = str_univ[:str_univ.find(' at ')].strip()
            edu_dict['University'] = str_univ[str_univ.find(' at ') + 4:].strip()
        elif 0 < str_univ_low.find('university') < str_univ.find('('):
            edu_dict['University'] = str_univ[:str_univ.find('(')].strip()
            if str_univ[str_univ.find('(') + 1:].strip(') ').isdigit():
                edu_dict['Year'] = str_univ[str_univ.find('(') + 1:].strip(') ')

        str_univ = edu_dict['University'] if 'University' in edu_dict else ''
        str_univ_low = str_univ.lower()
        if str_univ.endswith(' of'):
            edu_dict['University'] = ''
        elif 'school' in str_univ_low:
            edu_dict['School'] = edu_dict['University'].strip()
            edu_dict['University'] = ''
            if edu_dict['School'].lower().find('school') < edu_dict['School'].find('('):
                # "Europe Asia Business School (under aegis of Educatis University",
                edu_dict['School'] = edu_dict['School'][:edu_dict['School'].find('(')].strip()
        elif 'college' in str_univ_low and 'university' not in str_univ_low:
            edu_dict['College'] = str_univ
            edu_dict['University'] = ''
        elif str_univ.find('(') < str_univ_low.find('university') < str_univ.find(')'):
            # Institute of  Science ( Mumbai University)
            edu_dict['College'] = str_univ[:str_univ.find('(')].strip()
            edu_dict['University'] = str_univ[str_univ.find('(') + 1:str_univ.find(')')].strip()

        # -------------------- Degeree ---------------------
        str_degree = edu_dict['Degree']
        str_degree_words = str_degree.split()
        if 0 < str_degree.find('in the year') < str_degree.find('from'):
            # "B.Com in the year 2005 from Mumbai University"
            edu_dict['Degree'] = str_degree[:str_degree.find('in the year')].strip()
            edu_dict['Year'] = str_degree[str_degree.find('in the year') + 11:str_degree.find('from')].strip()
            edu_dict['University'] = str_degree[str_degree.find('from') + 4:].strip()
        elif str_degree.find('(') < str_degree.lower().find('university') < str_degree.find(')'):
            edu_dict['Degree'] = str_degree[:str_degree.find('(')].strip()
            edu_dict['University'] = str_degree[str_degree.find('(') + 1:str_degree.find(')')].strip()
        elif 0 < str_degree.find('from') < str_degree.find('with') < str_degree.find('year'):
            # Bachelor of Arts in Political Science from Mumbai University with Second Class - year 1999
            edu_dict['Degree'] = str_degree[:str_degree.find('from')].strip()
            edu_dict['University'] = str_degree[str_degree.find('from') + 4:str_degree.find('with')].strip()
            edu_dict['Year'] = str_degree[str_degree.find('year') + 4:].strip()
        elif 0 < str_degree.find('from') < str_degree.find('in year'):
            # S.S.C from O.L.P.S securing Distinction in year 2000.
            edu_dict['Degree'] = str_degree[:str_degree.find('from')].strip()
            edu_dict['University'] = str_degree[str_degree.find('from') + 4:str_degree.find('in year')].strip()
            edu_dict['Year'] = str_degree[str_degree.find('in year') + 7:].strip('. ')
        elif 0 < str_degree.find('from') < str_degree.find('with'):
            edu_dict['Degree'] = str_degree[:str_degree.find('from')].strip()
            edu_dict['University'] = str_degree[str_degree.find('from') + 4:].strip()
        elif 0 < str_degree.find('from'):
            edu_dict['Degree'] = str_degree[:str_degree.find('from')].strip()
            temp = str_degree[str_degree.find('from') + 4:].strip()
            if temp.isdigit():
                pass
            elif 0 < temp.lower().find('college(') < temp.lower().find('university)'):
                # Lady Irwin College(Delhi University) from 2003
                edu_dict['College'] = temp[:temp.find('(')]
                edu_dict['University'] = temp[temp.find('(') + 1:temp.find(')')]
            elif 0 < temp.lower().find('college') < temp.find('(') and temp[-1] == ')':
                # "Nirmala Niketan College of Home Science (Year 2007)"
                edu_dict['College'] = temp[:temp.find('(')].strip()
                last_word = temp.replace('(', ' ').replace(')', ' ').split()[-1]
                if last_word.isdigit() and len(last_word) == 4:
                    edu_dict['Year'] = last_word
            elif 0 < temp.lower().find('university') < temp.find('(') and temp[-1] == ')':
                # "Osmania University (2000 Batch)"
                edu_dict['University'] = temp[:temp.find('(')].strip()
                temp_word = temp.replace('(', ' ').replace(')', ' ').split()
                for i in range(len(temp_word)):
                    if temp_word[i].isdigit() and len(temp_word[i]) == 4:
                        edu_dict['Year'] = temp_word[i]
                        break
            elif 'college' in temp.lower():
                edu_dict['College'] = temp
            elif 'university' in temp.lower() or edu_dict['University'] == '':
                edu_dict['University'] = temp
        elif len(str_degree_words) > 0 and str_degree_words[-1].isdigit() and len(str_degree_words[-1]) == 4:
            # "Bachelor of Management Studies 2008"
            edu_dict['Degree'] = str_degree[:-5].strip()
            if edu_dict['Year'] == '':
                edu_dict['Year'] = str_degree[-4:]
        elif '(Graduating in' in str_degree:
            # "Currently pursuing MA in Human Resource Management (Graduating in January 2019)"
            edu_dict['Degree'] = str_degree[:str_degree.index('(Graduating in')].strip()
            edu_dict['Year'] = str_degree[str_degree.index('(Graduating in') + 14:].strip(') ')
        if edu_dict['Degree'].lower().startswith('post graduate '):
            edu_dict['Degree'] = edu_dict['Degree'][14:]
            edu_dict['Graduation'] = 'Post Graduate'
        elif edu_dict['Degree'].lower().startswith('post graduation '):
            edu_dict['Degree'] = edu_dict['Degree'][16:]
            edu_dict['Graduation'] = 'Post Graduate'

        # ------------------ Graduation --------------------
        str_grad = edu_dict['Graduation']
        if 0 <= str_grad.lower().find('graduation') < str_grad.find('('):
            # Post Graduation ( Environmental Science)
            edu_dict['Graduation'] = str_grad[:str_grad.find('(')].strip()
            edu_dict['Degree'] = str_grad[str_grad.find('(') + 1:].strip(' )')
        elif 'diploma in' in edu_dict['Graduation'].lower():
            # "Post Graduate Diploma in Business Management"
            temp_list = edu_dict['Graduation'].lower().split('diploma in')
            edu_dict['Graduation'] = temp_list[0].strip()
            edu_dict['Degree'] = temp_list[1].strip()

        return edu_dict

    def update_field(data_dict, field_name, field_value, same_dict=True, same_univ=True):
        if same_dict:
            pass
        elif not same_univ and field_name == 'University':
            pass
        elif data_dict[field_name] != '':
            ret_edu.append(fix_dict(data_dict))
            data_dict = edu_line_org.copy()
        elif same_univ and field_name == 'University' and ('School' in data_dict or data_dict['College'] != ''):
            ret_edu.append(fix_dict(data_dict))
            data_dict = edu_line_org.copy()
        data_dict[field_name] = field_value.strip('. ')
        data_dict = fix_dict(data_dict)

        return data_dict

    if 'Education' not in data:
        return {}

    data_edu = data['Education']
    # print(data_edu)
    ret_edu = []

    edu_line_org = {'Degree': '',
                    'University': '',
                    'College': '',
                    'Graduation': '',
                    'Year': '',
                    'Marks': ''}

    # ---------------- pre-processing ----------------------
    new_lines = data_edu.splitlines()
    f_same_dict = True
    for line_ind in range(len(new_lines)):
        if len(new_lines[line_ind]) < 30:
            f_same_dict = False
            break

    if f_same_dict:
        start_text_list = new_lines
    else:
        start_text_list = [data_edu]

    lines_edu_list = []
    for k in range(len(start_text_list)):
        new_data = ''
        start_text_lines = start_text_list[k].splitlines()
        for line_ind in range(len(start_text_lines)):
            if start_text_lines[line_ind].startswith('Completed'):
                continue

            new_data += start_text_lines[line_ind].replace('Post-Graduation', 'Post Graduation').replace(',', '\n').\
                            replace('-', '\n').replace(': ', '\n') + '\n'

        lines_edu_list.append(new_data)

    # ----------------- extraction ----------------------
    for g_ind in range(len(lines_edu_list)):
        lines_edu = lines_edu_list[g_ind].splitlines()
        edu_line_dict = edu_line_org.copy()
        mark_univ = -2
        for line_ind in range(len(lines_edu)):
            if (any(s in lines_edu[line_ind].lower() for s in degree_list) or
                any(s in lines_edu[line_ind] for s in degree_list_case)) and \
                    all(s not in lines_edu[line_ind].lower() for s in degree_no_list) and \
                    all(s != lines_edu[line_ind] for s in degree_no_same_list):
                edu_line_dict = update_field(edu_line_dict, 'Degree', lines_edu[line_ind], f_same_dict)
                if 'from' in lines_edu[line_ind]:
                    mark_univ = line_ind
            elif any(s in lines_edu[line_ind].lower() for s in school_key_list) \
                    and all(s != lines_edu[line_ind].lower() for s in school_no_same_key_list) \
                    and all(s not in lines_edu[line_ind].lower() for s in school_no_key_list):
                if mark_univ + 1 == line_ind or mark_univ + 2 == line_ind:
                    edu_line_dict = update_field(edu_line_dict, 'University', lines_edu[line_ind], f_same_dict, False)
                else:
                    edu_line_dict = update_field(edu_line_dict, 'University', lines_edu[line_ind], f_same_dict, True)
                mark_univ = line_ind
            elif check_year(lines_edu[line_ind]):
                if line_ind > 0 and check_year(lines_edu[line_ind - 1]):
                    edu_line_dict['Year'] = ''
                edu_line_dict = update_field(edu_line_dict, 'Year', lines_edu[line_ind], f_same_dict)
            elif any(s in lines_edu[line_ind].lower() for s in ['graduation', 'graduate']):
                edu_line_dict = update_field(edu_line_dict, 'Graduation', lines_edu[line_ind], f_same_dict)
            elif check_mark(lines_edu[line_ind]):
                edu_line_dict = update_field(edu_line_dict, 'Marks', lines_edu[line_ind], f_same_dict)

        ret_dict = fix_dict(edu_line_dict)
        for ret_key in ret_dict:
            if ret_dict[ret_key] != '':
                ret_edu.append(ret_dict)
                break

    return {'Education Detail': ret_edu}


def update_experience(data):
    def check_date(text_date):
        # May 2017, Jul'17
        if ' ' in text_date:
            data_list = text_date.split()
        elif "'" in text_date:
            data_list = text_date.split("'")
        else:
            data_list = [text_date]

        if len(data_list) == 2:
            if data_list[0].lower() in month_long_list or data_list[0].lower() in month_short_list:
                if data_list[1].isdigit() and (len(data_list[1]) == 4 or len(data_list[1]) == 2):
                    return True
            elif data_list[0].lower() == 'present':
                return True
            elif data_list[0] == 'till' and data_list[1] == 'date':
                return True
        elif len(data_list) == 1:
            if data_list[0].lower() == 'present':
                return True

        return False

    def check_company(text_comp):
        if any(s in text_comp.lower() for s in ['pvt.', 'ltd.', 'ltd,', 'pvt ltd']) and 'is a' not in text_comp:
            return True

        return False

    def fix_dict(exp_dict):
        if "Company Name" in exp_dict:
            temp_comp = exp_dict["Company Name"]
            if 0 < temp_comp.find('Ltd.,') < temp_comp.find('(') < temp_comp.find('till') < temp_comp.find(')'):
                # "ETP International Pvt. Ltd., Mumbai, India (Jan 2015 till date)"
                exp_dict["Company Name"] = temp_comp[:temp_comp.find('Ltd.,') + 4].strip()
                exp_dict["Location"] = temp_comp[temp_comp.find('Ltd.,') + 5:temp_comp.find('(')].strip()
                exp_dict["Start Date"] = temp_comp[temp_comp.find('(') + 1:temp_comp.find('till')].strip()
                exp_dict["End Date"] = temp_comp[temp_comp.find('till') + 4:temp_comp.find(')')].strip()
                if exp_dict["End Date"] == 'date':
                    exp_dict["End Date"] = ''
            elif 0 < temp_comp.find('/') < temp_comp.find(',') and \
                    check_company(temp_comp[temp_comp.find('/') + 1: temp_comp.find(',')]):
                # "Manager HR & Administration / Delightful Foods Pvt. Ltd., Mumbai"
                exp_dict["Company Name"] = temp_comp[temp_comp.find('/') + 1: temp_comp.find(',')].strip()
                exp_dict['Designation'] = temp_comp[:temp_comp.find('/')].strip()
                exp_dict["Location"] = temp_comp[temp_comp.find(',') + 1:].strip()

        if 'End Date' in exp_dict:
            temp_end = exp_dict['End Date']
            if temp_end.lower().startswith('present'):
                # "Present (Recruitree.net)",
                exp_dict['End Date'] = 'Present'

        if 'Designation' in exp_dict:
            temp_des = exp_dict['Designation']
            if len(temp_des) > 30 and '.' in temp_des:
                exp_dict['Designation'] = temp_des.split('.')[0]

        return exp_dict

    def update_field(data_dict, field_name, field_value):
        if data_dict[field_name] != '':
            ret_exp.append(fix_dict(data_dict))
            data_dict = exp_line_org.copy()

        data_dict[field_name] = field_value.strip('. ')

        return data_dict

    if 'Experience' not in data:
        return {}

    data_exp = data['Experience']
    # print(data_exp)

    ret_exp = []

    exp_line_org = {'Company Name': '',
                    'Location': '',
                    'Tenure': '',
                    'Start Date': '',
                    'End Date': '',
                    'Designation': ''}

    data_exp_lines = data_exp.splitlines()
    exp_line_dict = exp_line_org.copy()

    for line_ind in range(len(data_exp_lines)):
        exp_line = data_exp_lines[line_ind]
        if exp_line.lower().startswith('company name:'):
            temp_data = exp_line[13:]
            exp_line_dict = update_field(exp_line_dict, 'Company Name', temp_data)
        elif check_company(exp_line):
            exp_line_dict = update_field(exp_line_dict, 'Company Name', exp_line)
        elif exp_line.lower().startswith('designation:'):
            temp_data = exp_line[12:]
            exp_line_dict = update_field(exp_line_dict, 'Designation', temp_data)
        elif exp_line.lower().startswith('executive:'):
            temp_data = exp_line[10:]
            exp_line_dict = update_field(exp_line_dict, 'Designation', temp_data)
        elif exp_line.lower().startswith('executive :'):
            temp_data = exp_line[11:]
            exp_line_dict = update_field(exp_line_dict, 'Designation', temp_data)
        elif exp_line.lower().startswith('employment date:'):
            temp_data = exp_line[16:]
            if 'till date' in temp_data:    # April 2013 till date.
                exp_line_dict = update_field(exp_line_dict, 'Start Date', temp_data[:temp_data.index('till date')])
            elif 'till' in temp_data:       # May 12 till April 2013.
                exp_line_dict = update_field(exp_line_dict, 'Start Date', temp_data[:temp_data.index('till')])
                exp_line_dict = update_field(exp_line_dict, 'End Date', temp_data[temp_data.index('till') + 4:])
        elif exp_line.count('-') == 1 and len(exp_line.split('-')) == 2 \
                and check_date(exp_line.split('-')[0]) and check_date(exp_line.split('-')[1]):
            exp_line_dict = update_field(exp_line_dict, 'Start Date', exp_line.split('-')[0])
            exp_line_dict = update_field(exp_line_dict, 'End Date', exp_line.split('-')[1])
        elif exp_line.lower().count(' to ') == 1 and len(exp_line.lower().split(' to ')) == 2 \
                and check_date(exp_line.lower().split(' to ')[0]) and check_date(exp_line.lower().split(' to ')[1]):
            # Jul'17 to Mar'18
            exp_line_dict = update_field(exp_line_dict, 'Start Date', exp_line.lower().split(' to ')[0].title())
            exp_line_dict = update_field(exp_line_dict, 'End Date', exp_line.lower().split(' to ')[1].title())

        elif any(s in exp_line for s in ['HR-', 'Manager', 'Senior HR', 'Human Resource -', "Admin."]):
            exp_line_dict = update_field(exp_line_dict, 'Designation', exp_line)
        elif 0 < exp_line.find(',') < exp_line.find('(') and exp_line[-1] == ')' and exp_line.count(',') == 1:
            # Mani Jewel, Andheri (Mumbai)
            exp_line_dict = update_field(exp_line_dict, 'Company Name', exp_line)

    ret_exp.append(fix_dict(exp_line_dict))

    return {'Experience Detail': ret_exp}


def extract_subfields(data):
    ret_name = update_name(data)
    data.update(ret_name)
    ret_address = update_address(data)
    data.update(ret_address)
    ret_education = update_education(data)
    data.update(ret_education)
    ret_experience = update_experience(data)
    data.update(ret_experience)
    # print(json.dumps(ret_experience, indent=4))

    return data
