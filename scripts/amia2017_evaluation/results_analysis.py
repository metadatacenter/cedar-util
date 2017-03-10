# Results analysis module

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cedar_util

def analyze_results(results_df_raw, results_df_annotated):
    print('Number of instances (raw): ' + str(results_df_raw.shape[0] / 3))
    print('Number of instances (annotated): ' + str(results_df_annotated.shape[0] / 3))

    #results_df['correct_baseline'] = results_df['correct_baseline'].astype(float)
    #results_df['correct_vr'] = results_df['correct_vr'].astype(float)
    results_df_raw['Baseline'] = results_df_raw['RR_baseline'].astype(float)
    results_df_raw['VR'] = results_df_raw['RR_vr'].astype(float)
    results_df_annotated['Baseline'] = results_df_annotated['RR_baseline'].astype(float)
    results_df_annotated['VR'] = results_df_annotated['RR_vr'].astype(float)

    results_df_grouped_raw = results_df_raw.groupby(results_df_raw['field'])
    results_df_grouped_annotated = results_df_annotated.groupby(results_df_annotated['field'])

    print(results_df_grouped_raw.describe())
    print(results_df_grouped_raw.mean())

    print(results_df_grouped_annotated.describe())
    print(results_df_grouped_annotated.mean())

    # Separate data into two different data frames to plot them

    # results_df_correct = results_df[['field', 'top1_value_baseline', 'correct_baseline',
    #                                  'top1_value_vr', 'correct_vr']].copy()
    # results_df_correct_grouped = results_df_correct.groupby(results_df['field'])

    results_df_RR_raw = results_df_raw[['field', 'top3_values_baseline', 'Baseline',
                                'top3_values_vr', 'VR']].copy()
    results_df_RR_annotated = results_df_annotated[['field', 'top3_values_baseline', 'Baseline',
                                        'top3_values_vr', 'VR']].copy()

    results_df_RR_grouped_raw = results_df_RR_raw.groupby(results_df_raw['field'])
    results_df_RR_grouped_annotated = results_df_RR_annotated.groupby(results_df_raw['field'])

    # Plots

    fig, axes = plt.subplots(nrows=1, ncols=2)

    results_df_RR_grouped_raw.mean().plot.bar(ax=axes[0])
    axes[0].set_ylabel("MRR")

    results_df_RR_grouped_annotated.mean().plot.bar(ax=axes[1])
    axes[1].set_ylabel("MRR")
    plt.show()



    # -----
    # # Initialize a new figure
    # fig, ax = plt.subplots()
    #
    # # Draw the graph
    # ax.plot(df['GDP_per_capita'], df['life_expectancy'], linestyle='', marker='o')
    #
    # # Set the label for the x-axis
    # ax.set_xlabel("GDP (per capita)")
    #
    # # Set the label for the y-axis
    # ax.set_ylabel("Life expectancy at birth")
    #

def analyze_results_from_file(file_path_raw, file_path_annotated):
    results_df_raw = pd.read_csv(file_path_raw)
    results_df_annotated = pd.read_csv(file_path_annotated)
    analyze_results(results_df_raw, results_df_annotated)

def get_dataframe_for_frequecy_plot(populated_fields, target_field_path):
    VR_SERVER = "https://valuerecommender.metadatacenter.orgx/"
    API_KEY = "8a1364f7-9331-4926-94bd-06d3c3af1534"
    TEMPLATE_ID = "https://repo.metadatacenter.orgx/templates/31338972-e0cd-4540-a0e3-ba809690bbab"
    recommendation = cedar_util.get_value_recommendation(VR_SERVER, TEMPLATE_ID, target_field_path, populated_fields,API_KEY)
    sample_value = []
    sample_score = []
    print(recommendation)
    for v in recommendation['recommendedValues']:
        sample_value.append(v['value'])
        sample_score.append(v['score'])
    results = np.column_stack((sample_value, sample_score))
    results_df = pd.DataFrame(results, columns=['value', 'score'])
    results_df['score'] = results_df['score'].astype(float)
    return results_df

def generate_frequency_plots():

    # No context
    populated_fields = [{'path': 'optionalAttribute.name', 'value': 'disease'}]
    target_field_path = 'optionalAttribute.value'
    context0_df = get_dataframe_for_frequecy_plot(populated_fields, target_field_path)

    # Sex
    populated_fields = [{'path': 'optionalAttribute.name', 'value': 'disease'}, {'path': 'sex', 'value': 'female'}]
    target_field_path = 'optionalAttribute.value'
    context1_df = get_dataframe_for_frequecy_plot(populated_fields, target_field_path)

    # Sex and tissue
    populated_fields = [{'path': 'optionalAttribute.name', 'value': 'disease'}, {'path': 'sex', 'value': 'female'}, {'path': 'tissue', 'value': 'lung'}]
    target_field_path = 'optionalAttribute.value'
    context2_df = get_dataframe_for_frequecy_plot(populated_fields, target_field_path)

    fig, axes = plt.subplots(nrows=1, ncols=3)

    context0_df.set_index(["value"],inplace=True)
    ax0 = context0_df.plot(kind='bar', ax=axes[0], rot=90, legend=False)
    ax0.set_ylim(0, 0.9)
    ax0.set_title('disease=?', fontsize=10)
    axes[0].set_ylabel("relevancy score")
    axes[0].set_xlabel("")

    context1_df.set_index(["value"], inplace=True)
    ax1 = context1_df.plot(kind='bar', ax=axes[1], rot=90, legend=False)
    ax1.set_ylim(0, 0.9)
    ax1.set_title('sex=female\ndisease=?', fontsize=10)
    #axes[1].set_ylabel("relevancy score")
    axes[1].set_xlabel("")

    context2_df.set_index(["value"], inplace=True)
    ax2 = context2_df.plot(kind='bar', ax=axes[2], rot=90, legend=False)
    ax2.set_ylim(0, 0.9)
    ax2.set_title('sex=female\ntissue=lung\ndisease=?', fontsize=10)
    #axes[2].set_ylabel("relevancy score")
    axes[2].set_xlabel("")

    #fig.tight_layout()
    plt.xlabel("")
    plt.show()

def main_analysis():
    file_path_raw = "results/2017-03-06_22_17_32/results_34000_6800_Check_raw.csv"
    file_path_annotated = "results/2017-03-05_20_44_04/results_35000_7000_Check_annotated.csv"
    analyze_results_from_file(file_path_raw, file_path_annotated)

def main_frequencies():
    generate_frequency_plots()


#if __name__ == "__main__": main_analysis()
if __name__ == "__main__": main_frequencies()










