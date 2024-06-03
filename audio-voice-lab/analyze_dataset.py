# analyze_wav_data.py
import os
import glob
import re
import pandas as pd
import plotly.express as px
from pathlib import Path
import random

def extract_info_from_pathnames(file_path):
    values = file_path.split("/")
    # ['dm-fake-audio-voices-data', 'DMDF_Voices_V2', 'Spanish', 'ElevenLabs', 'ElevenLabs_Vocoder_Custom', 'validation', 'ElevenLabs', 'Ko_fem_spk22_bk1', 'Ko_fem_spk22_bk1Audio_Spanish_Sample38.wav']

    dataset_version = values[2]
    language = values[3]
    generator_type = values[4]
    vocoder_type = values[5]
    dataset_type = values[6]
    datasource_name = values[7]
    speaker_name = values[8]

    # print(dataset_version, language, generator_type, vocoder_type, dataset_name, speaker_name)
    return dataset_version, language, generator_type, vocoder_type, dataset_type, datasource_name, speaker_name

def load_wav_files(base_dir):
    # # Use a glob pattern to recursively find all wav files under the base directory
    # wav_files = glob.glob(os.path.join(base_dir, '**', '*.wav'), recursive=True)

    # # Filter only validation files
    # validation_files = [file for file in wav_files if '/validation/' in file]

    validation_files = []
    
    # Use os.walk to traverse the directory structure
    for root, dirs, files in os.walk(base_dir):
        if 'validation' in root:
            for file in files:
                if file.endswith('.wav'):
                    validation_files.append(os.path.join(root, file))


    file_contents = []
    random.Random(4).shuffle(validation_files)
    # for file_path in validation_files[0:1000]:
    for file_path in validation_files:
        dataset_version, language, generator_type, vocoder_type, dataset_type, datasource_name, speaker_name = extract_info_from_pathnames(file_path)

        if("ljspeech" in speaker_name):
            continue
            
        result_dict = {
            "dataset_version": dataset_version,
            "language": language,
            "generator_type": generator_type,
            "vocoder_type": vocoder_type,
            "dataset_type": dataset_type,
            "datasource_name": datasource_name,
            "speaker_name": speaker_name,
            "pathname": file_path,
            "is_manipulated": False if generator_type == "Unmanipulated" else True
        }
        file_contents.append(result_dict)


    return file_contents




def create_pie_chart(df, column, filter_conditions=None, title=None, output_filename=None, output_directory='.', collapse_column=None, collapse_value=None, collapse_to=None):
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    if filter_conditions:
        for condition in filter_conditions:
            df = df.query(condition)

    # Collapse specified column values
    if collapse_column and collapse_value is not None and collapse_to is not None:
        df[collapse_column] = df[collapse_column].apply(lambda x: collapse_to if x != collapse_value else x)

    value_counts = df[column].value_counts().reset_index()
    value_counts.columns = [column, 'count']
    
    total_samples = value_counts['count'].sum()
    num_legend_items = len(value_counts)

    fig = px.pie(value_counts, values='count', names=column, 
                 title=title if title else f'Distribution of {column}',
                 hole=0.2)

    fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='white', width=1)))

    # Determine the number of columns for the legend
    if num_legend_items > 6:
        legend_orientation = "h"
        legend_x = 0.5
        legend_y = -0.1
        legend_title_text = None
    else:
        legend_orientation = "v"
        legend_x = 1
        legend_y = 0.5
        legend_title_text = column

    fig.update_layout(
        showlegend=True,
        legend_title_text=legend_title_text,
        legend=dict(
            x=legend_x,
            y=legend_y,
            xanchor="center" if legend_orientation == "h" else "left",
            yanchor="top" if legend_orientation == "h" else "middle",
            orientation=legend_orientation,
            bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            itemsizing='constant'  # To ensure items are equally sized
        ),
        paper_bgcolor='black',
        plot_bgcolor='black',
        title=dict(font=dict(color='white', size=12), x=0.5, xanchor='center'),
        font=dict(color='white'),
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[
            dict(
                text=f'Total Samples: {total_samples}',
                x=0.5,
                y=1.1,
                showarrow=False,
                font=dict(color='white', size=12),
                xref="paper",
                yref="paper"
            )
        ]
    )

    # Save the figure
    if output_filename:
        fig.write_image(os.path.join(output_directory, output_filename), scale=4)
    # fig.show()

def visualize_data(file_contents_df, output_directory):

    # Visualize the data: Pie chart for language breakdown for real data
    create_pie_chart(
        df=file_contents_df,
        column='is_manipulated',
        title='Real vs AI',
        output_filename='all_data_real_fake.png',
        output_directory=output_parent_dir
    )

    # Visualize the data: Pie chart for language breakdown for real data
    # create_pie_chart(
    #     df=file_contents_df,
    #     column='is_manipulated',
    #     filter_conditions=['language != "English"'],
    #     title='Real vs AI Non English',
    #     output_filename='all_data_real_fake_noneng.png',
    #     output_directory=output_parent_dir
    # )

    for is_ai in [False, True]:
        string_val = "Real" if is_ai == False else "Fake"

        # Visualize the data: Pie chart for language breakdown for real data
        create_pie_chart(
            df=file_contents_df,
            column='language',
            filter_conditions=[f'is_manipulated == {is_ai}'],
            title=f'Languages for {string_val} Data',
            output_filename=f'lang_{string_val}.png',
            output_directory=output_parent_dir
        )

        # # # Visualize the data: Pie chart for language breakdown for real data
        # create_pie_chart(
        #     df=file_contents_df,
        #     column='language',
        #     filter_conditions=[f'is_manipulated == {is_ai}', 'language != "English"'],
        #     title=f'Languages for Non-English {string_val} Data',
        #     output_filename=f'lang_znoneng_{string_val}.png',
        #     output_directory=output_parent_dir
        # )


        # Visualize the data: Pie chart for language breakdown for real data
        create_pie_chart(
            df=file_contents_df,
            column='datasource_name',
            filter_conditions=[f'is_manipulated == {is_ai}'],
            title=f'Datasources for {string_val} Data',
            output_filename=f'datasource_{string_val}.png',
            output_directory=output_parent_dir
        )

        # # Visualize the data: Pie chart for language breakdown for real data
        # create_pie_chart(
        #     df=file_contents_df,
        #     column='datasource_name',
        #     filter_conditions=[f'is_manipulated == {is_ai}', 'language != "English"'],
        #     title=f'Datsources for Non-English {string_val} Data',
        #     output_filename=f'datasource_znoneng_{string_val}.png',
        #     output_directory=output_parent_dir
        # )


        # Visualize the data: Pie chart for language breakdown for real data
        create_pie_chart(
            df=file_contents_df,
            column='generator_type',
            filter_conditions=[f'is_manipulated == {is_ai}'],
            title=f'Generators for {string_val} Data',
            output_filename=f'gen_{string_val}.png',
            output_directory=output_parent_dir
        )

        # # Visualize the data: Pie chart for language breakdown for real data
        # create_pie_chart(
        #     df=file_contents_df,
        #     column='generator_type',
        #     filter_conditions=[f'is_manipulated == {is_ai}', 'language != "English"'],
        #     title=f'Generators for Non-English {string_val} Data',
        #     output_filename=f'gen_znoneng_{string_val}.png',
        #     output_directory=output_parent_dir
        # )

        # # # Visualize the data: Pie chart for language breakdown for real data
        # create_pie_chart(
        #     df=file_contents_df,
        #     column='generator_type',
        #     filter_conditions=[f'is_manipulated == {is_ai}', 'language == "English"'],
        #     title=f'Generators for English {string_val} Data',
        #     output_filename=f'gen_zonlyeng_{string_val}.png',
        #     output_directory=output_parent_dir
        # )




        # Visualize the data: Pie chart for language breakdown for real data
        create_pie_chart(
            df=file_contents_df,
            column='vocoder_type',
            filter_conditions=[f'is_manipulated == {is_ai}'],
            title=f'Vocoders for {string_val} Data',
            output_filename=f'voc_{string_val}.png',
            output_directory=output_parent_dir
        )

        # # # Visualize the data: Pie chart for language breakdown for real data
        # create_pie_chart(
        #     df=file_contents_df,
        #     column='vocoder_type',
        #     filter_conditions=[f'is_manipulated == {is_ai}', 'language != "English"'],
        #     title=f'Vocoders for Non-English {string_val} Data',
        #     output_filename=f'voc_znoneng_{string_val}.png',
        #     output_directory=output_parent_dir
        # )


        # Visualize the data: Pie chart for speaker breakdown (unknown vs known)
        create_pie_chart(
            df=file_contents_df,
            column='speaker_name',
            filter_conditions=[f'is_manipulated == {is_ai}'],
            title=f'Speakers (Unknown vs Known) {string_val}',
            output_filename=f'speaker_{string_val}.png',
            output_directory=output_parent_dir,
            collapse_column='speaker_name',
            collapse_value='Unknown_ID',
            collapse_to='known'        
        )

        # create_pie_chart(
        #     df=file_contents_df,
        #     column='speaker_name',
        #     filter_conditions=[f'is_manipulated == {is_ai}', 'language != "English"'],
        #     title=f'Speakers Non-English (Unknown vs Known) {string_val}',
        #     output_filename=f'speaker_znoneng_{string_val}.png',
        #     output_directory=output_parent_dir,
        #     collapse_column='speaker_name',
        #     collapse_value='Unknown_ID',
        #     collapse_to='known'        
        # )

# Define the base directory
base_dir = 'deepmedia-datasets-public/audio-voice-lab/240602-52933D'
output_parent_dir = 'visualizations/240602-52933D/dataset'

# Load the wav files
file_contents = load_wav_files(base_dir)

# Convert the list of dictionaries to a DataFrame
file_contents_df = pd.DataFrame(file_contents)

# Visualize the data
visualize_data(file_contents_df, output_parent_dir)

print(f"Loaded {len(file_contents_df)} WAV files.")
