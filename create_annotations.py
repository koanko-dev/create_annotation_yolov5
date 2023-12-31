import json
import os


class_name_to_id_mapping = {
    "A1_구진_플라크": 0,
    "A2_비듬_각질_상피성잔고리": 1,
    "A3_태선화_과다색소침착": 2,
    "A4_농포_여드름": 3,
    "A5_미란_궤양": 4,
    "A6_결절_종괴": 5,
    }

train_root_dir_name = 'skin_disease/train/cat/A2_비듬_각질_상피성잔고리'
val_root_dir_name = 'skin_disease/val/cat/A2_비듬_각질_상피성잔고리'
train_result_dir_name = 'skin_disease/train/cat/A2_비듬_각질_상피성잔고리/labels'
val_result_dir_name = 'skin_disease/val/cat/A2_비듬_각질_상피성잔고리/labels'

def extract_info_from_json(json_file_name):
    f = open(json_file_name)

    print('converting target: ', json_file_name)

    loaded_file = json.load(f)

    info_dict = {}
    info_dict['bboxes'] = []

    img_size = [1920, 1080, 3]
    info_dict['image_size'] = tuple(img_size)
    info_dict['filename'] = json_file_name[:-5].split('/')[-1] + '.jpg'

     # search box indexes in 'labelingInfo'
    labeling_info = loaded_file['labelingInfo']
    box_loc_idxes = []
    for idx, shape in enumerate(labeling_info):
        if shape.get('box'):
            box_loc_idxes.append(idx)

    for box_loc_idx in box_loc_idxes:
        box = loaded_file['labelingInfo'][box_loc_idx]['box']
        box_location = box['location'][0]

        bbox = {}
        bbox["class"] = box['label']
        bbox['xmin'] = int(box_location['x'])            
        bbox['ymin'] = int(box_location['y'])            
        bbox['width'] = int(box_location['width'])            
        bbox['height'] = int(box_location['height'])            

        info_dict['bboxes'].append(bbox)
    
    f.close()
    return info_dict


def convert_to_yolov5(info_dict, result_dir_name):
    print_buffer = []

    for b in info_dict["bboxes"]:
        try:
            class_id = class_name_to_id_mapping[b["class"]]
        except KeyError:
            print("Invalid Class. Must be one from ", class_name_to_id_mapping.keys())
   
        min_x = b["xmin"]
        min_y = b["ymin"]
        width = b["width"]
        height = b["height"]

        center_x = (min_x + min_x + width) / 2
        center_y = (min_y + min_y + height) / 2
        
        image_w, image_h, image_c = info_dict["image_size"]  
        center_x /= image_w
        center_y /= image_h
        width /= image_w
        height /= image_h
        
        print_buffer.append("{} {} {} {} {}".format(class_id, center_x, center_y, width, height))
        
    save_file_name = os.path.join(result_dir_name, info_dict["filename"].replace("jpg", "txt"))
    print("\n".join(print_buffer), file=open(save_file_name, "w"))


# train json -> txt
train_annotations = [os.path.join(train_root_dir_name, x) for x in os.listdir(train_root_dir_name) if x[-4:] == "json"]
train_annotations.sort()

for ann in train_annotations:
    info_dict = extract_info_from_json(ann)
    convert_to_yolov5(info_dict, train_result_dir_name)

# val json -> txt
val_annotations = [os.path.join(val_root_dir_name, x) for x in os.listdir(val_root_dir_name) if x[-4:] == "json"]
val_annotations.sort()

for ann in val_annotations:
    info_dict = extract_info_from_json(ann)
    convert_to_yolov5(info_dict, val_result_dir_name)

print('txt file saved!')