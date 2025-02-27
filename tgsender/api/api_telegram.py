import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from pyrogram import Client, types

from .. import utils
from ..mediainfo import ffprobe


def logging_config():
    log_file_name = "api_telegram"
    logfilename = "log-" + log_file_name + ".txt"
    logging.basicConfig(
        level=logging.INFO,
        format=" %(asctime)s-%(levelname)s-%(message)s",
        handlers=[logging.FileHandler(logfilename, "w", "utf-8")],
    )
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter(" %(asctime)s-%(levelname)s-%(message)s")
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)


def ensure_connection():

    if Path("user.session").exists():
        try:
            with Client(
                "user", workdir=Path("user.session").absolute().parent
            ) as app:
                message = app.send_message(
                    "me", text="telegram filesender-Connected..."
                )
                message.delete()
            return
        except:
            print("Delete Session file and try again.")

    while True:
        try:
            api_id = int(input("Enter your api_id: "))
            api_hash = input("Enter your api_hash: ")

            with Client(
                "user",
                api_id,
                api_hash,
                workdir=Path("user.session").absolute().parent,
            ) as app:
                message = app.send_message(
                    "me", text="telegram filesender-Connected..."
                )
                message.delete()
            return
        except:
            print("\nError. Try again.\n")
            pass


# Keep track of the progress while uploading
def progress(current, total):

    stringa = f"{current * 100 / total:.1f}%"
    sys.stdout.write(stringa)
    sys.stdout.flush()
    sys.stdout.write("\b" * len(stringa))
    sys.stdout.flush()


def send_video(chat_id, file_path, caption):

    logging.info("Sending video...")
    try:
        metadata = ffprobe(file_path).get_output_as_dict()
        metadata_streams = metadata["streams"]
        video_metadata = metadata_streams[0]
    except:
        # case of error, show all file metadata
        print(file_path)
        print(ffprobe(file_path).get_output_as_dict())
        metadata = ffprobe(file_path).get_output_as_dict()
        metadata_streams = metadata["streams"]
        video_metadata = metadata_streams[0]
    try:
        width = video_metadata["width"]
    except:
        video_metadata = metadata_streams[1]
    try:
        width = video_metadata["width"]
        height = video_metadata["height"]
        duration = int(float(metadata["format"]["duration"]))
    except Exception as e:
        logging.error(f"File Error: {file_path}.\napi_telegram.py line 63")
        raise ValueError(e)
    thumb = utils.create_thumb(file_path)

    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.send_video(
            chat_id,
            file_path,
            caption=caption,
            progress=progress,
            supports_streaming=True,
            width=width,
            height=height,
            duration=duration,
            thumb=thumb,
        )
    os.remove(thumb)
    return return_


def send_sticker(chat_id, sticker):

    logging.info("Sending sticker...")
    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.send_sticker(chat_id, sticker)
    return return_


def send_photo(chat_id, file_path, caption):

    logging.info("Sending photo...")
    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.send_photo(
            chat_id, file_path, caption=caption, progress=progress
        )
    return return_


def send_audio(chat_id, file_path, caption):
    logging.info("Sending audio...")
    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.send_audio(
            chat_id, file_path, caption=caption, progress=progress
        )
    return return_


def send_document(chat_id, file_path, caption):
    logging.info("Sending document...")
    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.send_document(
            chat_id, file_path, caption=caption, progress=progress
        )
    return return_


def send_message(chat_id, text):

    logging.info("Sending message...")
    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.send_message(
            chat_id, text=text, disable_web_page_preview=True
        )
    return return_


def pin_chat_message(chat_id, message_id):

    logging.info("Pinning message...")
    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.pin_chat_message(
            chat_id, message_id=message_id, both_sides=True
        )
    return return_


def get_messages(chat_id, message_ids):

    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.get_messages(chat_id, message_ids)
    return return_


def get_history(chat_id):

    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.get_history(chat_id)
    return return_


def get_list_media_doc(list_dict_sent_doc):
    """
    Generates a list of "inputmediadocument"
     from a list of 'return of sent files'.
    Used to forward files in album format with 'send_media_group' method

    Args:
        list_dict_sent_doc (list):
            List of returns from many files sent by the send_document method

    Returns:
        list: list of InputMediaDocument pyrogram type,
               necessary to send_media_group method
    """

    list_media_doc = []
    for dict_sent_doc in list_dict_sent_doc:
        file_id = dict_sent_doc["file_id"]
        caption = dict_sent_doc["caption"]
        media = types.InputMediaDocument(media=file_id, caption=caption)

        list_media_doc.append(media)
    return list_media_doc


def send_media_group(chat_id, list_media):

    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.send_media_group(chat_id, media=list_media)
    return return_


def delete_messages(chat_id, list_message_id):

    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.delete_messages(
            chat_id=chat_id, message_ids=list_message_id
        )
    return return_


def send_file(dict_file_data, chat_id, time_limit=99):

    file_path = dict_file_data["file_output"]
    description = dict_file_data["description"]
    file_extension = Path(file_path).suffix
    if file_extension == ".mp4":
        type_file = "video"
    elif file_extension == ".mp3":
        type_file = "audio"
    elif file_extension in [".png", ".jpg", ".jpeg", ".gif"]:
        type_file = "photo"
    else:
        type_file = "document"

    if type_file == "video":
        return_ = send_video(
            chat_id=chat_id,
            file_path=file_path,
            caption=description,
        )
    elif type_file == "audio":
        return_ = send_audio(
            chat_id=chat_id,
            file_path=file_path,
            caption=description,
        )
    elif type_file == "photo":
        return_ = send_photo(
            chat_id=chat_id,
            file_path=file_path,
            caption=description,
        )
    elif type_file == "document":
        return_ = send_document(
            chat_id=chat_id,
            file_path=file_path,
            caption=description,
        )

    return return_


def send_files(list_dict, chat_id, time_limit=20):
    """Sends a series of files to the same chat_id

    Args:
        list_dict (list): list of dict. dict with keys:
            file_path=Absolute file_path
            description=file description
            file_output=file name for log
    """

    list_return = []
    len_list_dict = len(list_dict)
    for index, d in enumerate(list_dict):
        order = index + 1
        file_path = d["file_output"]

        if not Path(file_path).exists():
            logging.error(f"file not exist. {file_path}")
            continue

        now = datetime.now()
        dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
        print(f"{dt_string}-{order}/{len_list_dict} Uploading: {file_path}")
        logging.info(f"{order}/{len_list_dict} Uploading: {file_path}")

        file_extension = Path(file_path).suffix
        description = d["description"]

        if file_extension == ".mp4":
            type_file = "video"
        elif file_extension == ".mp3":
            type_file = "audio"
        elif file_extension in [".png", ".jpg", ".jpeg", ".gif"]:
            type_file = "photo"
        else:
            type_file = "document"

        while True:
            try:
                if type_file == "video":
                    return_ = send_video(
                        chat_id=chat_id,
                        file_path=file_path,
                        caption=description,
                    )
                elif type_file == "audio":
                    return_ = send_audio(
                        chat_id=chat_id,
                        file_path=file_path,
                        caption=description,
                    )
                elif type_file == "photo":
                    return_ = send_photo(
                        chat_id=chat_id,
                        file_path=file_path,
                        caption=description,
                    )
                elif type_file == "document":
                    return_ = send_document(
                        chat_id=chat_id,
                        file_path=file_path,
                        caption=description,
                    )
                break
            except Exception as e:
                print(e)
                print("\nError. Trying again...")
                time.sleep(30)
                continue
        list_return.append(return_)
    return list_return


def create_channel(title, description):

    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_chat = app.create_channel(title=title, description=description)
    chat_id = return_chat.id
    return chat_id


def add_chat_members(chat_id, user_ids):

    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_chat = app.add_chat_members(chat_id=chat_id, user_ids=user_ids)


def promote_chat_members(chat_id, user_ids):

    with Client("user", workdir=Path("user.session").absolute().parent) as app:

        privileges_config = types.ChatPrivileges(
            can_change_info=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True,
            can_promote_members=True,
        )

        for user_id in user_ids:
            app.promote_chat_member(
                chat_id=chat_id, user_id=user_id, privileges=privileges_config
            )


def set_chat_description(chat_id, description):

    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        app.set_chat_description(chat_id=chat_id, description=description)


def export_chat_invite_link(chat_id):

    with Client("user", workdir=Path("user.session").absolute().parent) as app:
        return_ = app.export_chat_invite_link(chat_id=chat_id)

    return return_


def get_template(folder_path_descriptions, file_name):

    template_path = Path(folder_path_descriptions) / file_name
    if not template_path.exists():
        template_path = (
            Path(__file__).absolute().parent.parent / "template" / file_name
        )
    if not template_path.exists():
        raise FileNotFoundError(f"{template_path=}")
    return template_path


def get_channel_title(folder_path_descriptions):

    header_project_name = "header_project.txt"
    header_project_path = get_template(
        folder_path_descriptions, header_project_name
    )
    print(f"\n{header_project_path=}\n")
    channel_info_stringa = utils.get_txt_content(header_project_path)
    list_channel_info = channel_info_stringa.split("\n")

    title = list_channel_info[0]
    return title


def get_channel_description(chat_invite_link, folder_path_descriptions):

    header_template_name = "header_project.txt"
    header_template_path = get_template(
        folder_path_descriptions, header_template_name
    )

    channel_info_stringa = utils.get_txt_content(header_template_path)
    list_channel_info = channel_info_stringa.split("\n")

    description = "\n".join(list_channel_info[1:])
    description = description.replace("{chat_invite_link}", chat_invite_link)
    return description


def get_list_adms(channel_adms: str):

    if not channel_adms:
        return []
    channel_adms_stringa_list = channel_adms.split(",")
    list_adms = []
    for line in channel_adms_stringa_list:
        list_adms.append(line.strip())
    return list_adms
