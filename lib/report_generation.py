
import markdown
import matplotlib.pyplot as plt

class ReportGenerator:
   def __init__(self):
       pass

   def generate_report(self, analysis_results):
       # ���͌��ʂ���Ƀ��|�[�g�𐶐�
       pass

   def save_report(self, report, file_path):
       with open(file_path, 'w') as file:
           file.write(report)

   def save_visualizations(self, visualizations, folder_path):
       for viz_name, viz_data in visualizations.items():
           plt.figure()
           # �O���t���쐬
           plt.savefig(f"{folder_path}/{viz_name}.png")
           plt.close()
