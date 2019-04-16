import csv


def write_train(one_line_pixels):
    with open('data/train.csv', 'a+') as brain_data_train:
        brain_csv = csv.writer(brain_data_train, delimiter=',', quotechar='"', lineterminator='\n',
                               quoting=csv.QUOTE_MINIMAL)
        brain_csv.writerow(one_line_pixels)


def write_test(one_line_pixels):
    with open('data/test.csv', 'a+') as brain_data_test:
        brain_csv = csv.writer(brain_data_test, delimiter=',', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        brain_csv.writerow(one_line_pixels)
