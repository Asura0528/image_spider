import os
import decompress


def deal_file(file_list_dir, data_name):
    for file_list in file_list_dir:
        v_count = 0
        gif_count = 0
        other_count = 0
        count = 0
        rm_count = 0
        other_list = []
        rm_list = []
        file_dir_path = os.path.join(path, file_list)
        file_list = os.listdir(file_dir_path)
        file_list.sort()
        print("=====开始重命名文件夹" + file_dir_path + "中文件=====")
        for file in file_list:
            old_dir = os.path.join(file_dir_path, file)  # 原来的文件路径
            file_name = os.path.splitext(file)[0]
            filetype = os.path.splitext(file)[1]  # 文件扩展名
            if filetype == '':  # 无文件类型为文件夹，递归执行名称查询
                deal_file([old_dir], data_name)
            if file_name in ('gteman', '加入艾薇福利社会员享永久福利') \
                    or file == 'gteman.jpg' \
                    or filetype.lower() in ('.html', '.url', '.txt'):
                rm_count += 1
                os.remove(old_dir)
                rm_list.append(file_name)
                continue
            if filetype.lower() in ('.jpg', '.png'):
                pre_name = 'IMG'
                count += 1
                str_name = "{}_{:03}{}".format(pre_name, count, filetype)
            elif filetype.lower() in ('.mp4', '.mov'):
                pre_name = 'V'
                v_count += 1
                str_name = "{}_{:03}{}".format(pre_name, v_count, filetype)
            elif filetype.lower() == '.gif':
                pre_name = 'GIF'
                gif_count += 1
                str_name = "{}_{:03}{}".format(pre_name, gif_count, filetype)
            elif filetype.lower() == '.7zz':
                other_count += 1
                filetype = '.7z'
                str_name = "{:03}{}".format(other_count, filetype)
            elif filetype.lower() == '.tar':
                count += 1
                filetype = '.tar'
                str_name = "{:03}{}".format(count, filetype)
            elif filetype.lower() in ('.7z',):
                print("解压文件" + file + "开始")
                decompress.decompress(old_dir, file, 'gteman.com')
                str_name = file_name + filetype
                print("解压文件" + file + "结束")
            else:
                other_count += 1
                str_name = file_name + filetype
                other_list.append(str_name)
            new_dir = os.path.join(file_dir_path, str_name)  # 新的文件路径
            os.rename(old_dir, new_dir)  # 重命名
        print("重命名图片数：" + str(count) +
              "\n重命名视频数：" + str(v_count) +
              "\n重命名动图数：" + str(gif_count) +
              "\n其他重命名：" + str(other_count) + "|" + ",".join(other_list) +
              "\n删除文件数：" + str(rm_count) + "|" + ",".join(rm_list))
        print("=====重命名文件夹" + file_dir_path + "中文件结束=====")


if __name__ == '__main__':
    name = 'rioko凉凉子'
    path = r'\\192.168.0.101\39008675\我的图片\{}'.format(name)
    deal_file(os.listdir(path), name)
