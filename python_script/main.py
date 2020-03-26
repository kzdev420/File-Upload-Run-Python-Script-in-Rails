
from extractor import ResumeExtractor
from func import *
import json
import sys


if __name__ == '__main__':
    if len(sys.argv) == 2:
        file_name = sys.argv[1]
    else:
        file_name = 'samples/BA/ 021 PRAVIN DESHMUKH-.pdf'

    class_resume = ResumeExtractor()

    # _, _, join_list = get_file_list('../samples')
    # file_name = join_list[50]

    ret = class_resume.extract(file_name)
    print("File: " + file_name + '\n')
    print(json.dumps(ret, indent=4))

    # for key in sorted(ret):
    #     print(key, ret[key])
