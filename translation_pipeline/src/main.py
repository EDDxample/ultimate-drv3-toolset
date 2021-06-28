import json, os
from translation_pipeline.src import utils, spc, stx

def extract_text(filename):
    """
    Executes steps 1, 2 and 3 to get the merged dialogues.
    Stores them in "./translation_pipeline/pipeline/3_merged_dialogues/"
    """
    spc_to_stxs(filename)   # step 1
    stxs_to_jsons(filename) # step 2
    merge_jsons(filename)   # step 3

def patch_text(filename):
    """
    Executes steps 4 and 5 to repack the texts into the final SPC
    Stores them in "./translation_pipeline/pipeline/5_output_SPC/"
    """
    mega_json_to_stxs(filename) # step 4
    stxs_to_spc(filename)       # step 5


# step 1
def spc_to_stxs(filename):
    print(f'extracting .stx files from {filename}.spc...')
    
    spc.extract(filename)

    print('done.')


# step 2
def stxs_to_jsons(filename):
    print('extracting dialogues from .stx files and translating them...')

    stx_path = f'{utils.STEP_1_PATH}/{filename}/'
    
    subfiles = [ f for f in os.listdir(stx_path) if os.path.isfile(os.path.join(stx_path, f)) ]
    for i, subfilename in enumerate(subfiles):
        print(f'{i+1}/{len(subfiles)} - {subfilename}')
        stx_to_json(filename, subfilename)

    print('done.')

def stx_to_json(filename, subfilename):
    en, gt = stx.extract(f'{utils.STEP_1_PATH}/{filename}/{subfilename}')
    data = []

    for i in range(len(en)):
        data.append({ 'en': en[i], 'gt': gt[i], 'es': gt[i] })

    utils.ensure_paths(f'{utils.STEP_2_PATH}/{filename}/{subfilename}.json')
    with open(f'{utils.STEP_2_PATH}/{filename}/{subfilename}.json', 'w', encoding='utf-16') as file_json:
        json.dump(data, file_json, indent=2, ensure_ascii=False)


# step 3
def merge_jsons(filename):
    print('merging .json files...')
    
    json_path = f'{utils.STEP_2_PATH}/{filename}/'
    out = {}
    
    subfiles = [ f for f in os.listdir(json_path) if os.path.isfile(os.path.join(json_path, f)) ]
    for subfile in subfiles:
        subfilename = subfile.replace('.stx.json', '')
        with open(f'{utils.STEP_2_PATH}/{filename}/{subfile}', 'r', encoding='utf-16') as curfile:
            text = json.load(curfile)
            out[subfilename] = { 'text': text, 'translated': False }
    
    utils.ensure_paths(f'{utils.STEP_3_PATH}/{filename}.json')
    with open(f'{utils.STEP_3_PATH}/{filename}.json', 'w', encoding='utf-16') as file_json:
        json.dump(out, file_json, indent=2, ensure_ascii=False)

    print('done.')


# step 4
def mega_json_to_stxs(filename):
    print(f'converting {filename}.json into .stx files...')

    with open(f'{utils.STEP_3_PATH}/{filename}.json', 'r', encoding='utf-16') as mj_file:
        mj = json.load(mj_file)
        translated_lines = 0
        total_lines = 0
        for key in mj:
            value = mj[key]
            
            # stats
            line_count = len(value['text'])
            total_lines += line_count
            if value['translated']: translated_lines += line_count

            # stx convertion
            lines = list(map(lambda texts: texts['es'], value['text']))
            data = stx.repack(lines)
            utils.ensure_paths(f'{utils.STEP_4_PATH}/{filename}/{key}.stx')
            with open(f'{utils.STEP_4_PATH}/{filename}/{key}.stx', 'wb') as outfile:
                outfile.write(data)

        print(f'{filename}: {translated_lines} out of {total_lines} lines. {translated_lines / total_lines * 100:.2f}%')
    
    print('done.')


# step 5
def stxs_to_spc(filename):
    print('merging .stx files...')

    stx_path = f'{utils.STEP_4_PATH}/{filename}/'
    subfiles = [ f for f in os.listdir(stx_path) if os.path.isfile(os.path.join(stx_path, f)) ]
    data = spc.repack(filename, subfiles)
    utils.ensure_paths(f'{utils.STEP_5_PATH}/{filename}.spc')
    with open(f'{utils.STEP_5_PATH}/{filename}.spc', 'wb') as spc_file:
        spc_file.write(data)
        
    print('done.')
