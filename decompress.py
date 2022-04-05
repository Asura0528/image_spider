import zipfile
import py7zr


def decompress(path_name, file_name, pwd):
    suffix = path_name.rsplit('.', 1)[1]
    if suffix == 'zip':
        if zipfile.is_zipfile(path_name):
            try:
                with zipfile.ZipFile(path_name) as zip_f:
                    zip_f.extractall(path_name.rsplit(".zip")[0])
            except Exception as e:
                print('Error when uncompress file! info: ', e)
                return False
            else:
                return True
        else:
            print('This is not a true zip file!')
            return False
    if suffix == '7z':
        if py7zr.is_7zfile(path_name):
            try:
                # d_name为特殊处理的密码，文件名字的一部分
                with py7zr.SevenZipFile(path_name, password=pwd, mode='r') as sevenZ_f:
                    sevenZ_f.extractall(path_name.rsplit(file_name)[0])
            except Exception as e:
                print('Error when uncompress file! info: ', e)
                return False
            else:
                return True
        else:
            print('This is not a true 7z file!')
            return False
