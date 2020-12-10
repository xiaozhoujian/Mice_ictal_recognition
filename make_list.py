import os
import random


def split_data(data_path, train_ratio=0.75):
    items = os.listdir(data_path)
    video_num = len(items)
    random.shuffle(items)
    train_samples = sorted(items[:int(video_num*train_ratio)])
    test_samples = sorted(items[int(video_num*train_ratio):])
    return train_samples, test_samples


def write2file(samples, source_path, file_obj, class_label):
    for sample in samples:
        line = os.path.join(source_path, sample + ' #{}\n'.format(class_label))
        file_obj.write(line)


def make_train_test(case_path, control_path, train_txt, test_case_txt, test_ctl_txt, train_ratio=0.75):
    # for ori_path, fold, items in os.walk(epilepsy_path):
    train_case_samples, test_case_samples = split_data(case_path, train_ratio)

    # for ori_path, fold, items in os.walk(normal_path):
    train_control_samples, test_control_samples = split_data(control_path, train_ratio)

    print('Making train list')
    file = open(train_txt, 'w')
    write2file(train_control_samples, control_path, file, '0')
    write2file(train_case_samples, case_path, file, '1')
    file.close()
    print('Train list done')

    print('Making test list')
    control_file_obj = open(test_ctl_txt, 'w')
    write2file(test_control_samples, control_path, control_file_obj, '0')
    control_file_obj.close()
    case_file_obj = open(test_case_txt, 'w')
    write2file(test_case_samples, case_path, case_file_obj, '1')
    case_file_obj.close()
    print('Test list done')


def make_new_test():
    test_name = 'dataset/mice_labels/test_C22_0930.txt'
    dir_path = '../dataset/mice/C22_0930/'
    case_path = 'pre_case'
    control_path = 'pre_control'

    print('Making list {}'.format(test_name))
    file = open(test_name, 'w')

    if os.path.exists(os.path.join(dir_path, control_path)):
        v_control_spl = sorted(os.listdir(os.path.join(dir_path, control_path)))
        for i in v_control_spl:
            line = os.path.join(control_path, i[:-4]) + ' #0'
            file.write(line)
            file.write('\n')

    if os.path.exists(os.path.join(dir_path, case_path)):
        v_case_spl = sorted(os.listdir(os.path.join(dir_path, case_path)))
        for i in v_case_spl:
            line = os.path.join(case_path, i[:-4])+' #1'
            file.write(line)
            file.write('\n')
    file.close()
    print('list {} is done'.format(test_name))


def main():
    make_train_test()
    # make_new_test()
    

if __name__ == "__main__":
    main()
