import zipfile
import os
import shutil
import bpy

def install_aces(use_zip_file=False, zip_file=None):
    # set up empty folder for backup
    cs_folder = get_blender_cs_folder()
    aces_backup = set_backup_folder(cs_folder, 'aces_backup')
    filmic_backup = set_backup_folder(cs_folder, 'filmic_backup')

    # move filmic file to backup folder
    move_folder_files(cs_folder, filmic_backup)
    # unzip and move aces files
    if not use_zip_file or not zip_file:
        unzip_to_cs_folder(zip_file, cs_folder)
    else:
        move_folder_files(aces_backup, cs_folder)


def rollback_filmic():
    cs_folder = get_blender_cs_folder()
    aces_backup = set_backup_folder(cs_folder, 'aces_backup')
    filmic_backup = set_backup_folder(cs_folder, 'filmic_backup')
    # move aces file to backup folder
    move_folder_files(cs_folder, aces_backup)
    # move filmic file to cs folder
    move_folder_files(filmic_backup, cs_folder)


def get_blender_cs_folder():
    bl_data_path = bpy.utils.system_resource("DATAFILES")
    cs_folder = os.path.join(bl_data_path, 'colormanagement')

    return cs_folder


def set_backup_folder(dirname, name):
    if not os.path.exists(os.path.join(dirname, name)):
        os.makedirs(os.path.join(dirname, name))
    return os.path.join(dirname, name)


def move_folder_files(old_path, new_path):
    filelist = os.listdir(old_path)  # 列出该目录下的所有文件,listdir返回的文件列表是不包含路径的。
    for file in filelist:
        if file not in {'aces_backup', 'backup'}:
            src = os.path.join(old_path, file)
            dst = os.path.join(new_path, file)
            shutil.move(src, dst)


def unzip_to_cs_folder(zip_path, cs_folder):
    dirname = os.path.dirname(zip_path)
    file_name = os.path.basename(zip_path)

    file_extracting = zipfile.ZipFile(zip_path)
    file_extracting.extractall(dirname)
    aces_1_2 = os.path.join(dirname, file_name, 'aces_1.2')

    move_folder_files(aces_1_2, cs_folder)
