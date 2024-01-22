from osw_confidence_metric  import OSWConfidenceMetric
class DifferentClass:
    def __init__(self):
        pass

    def my_function(self):
        # Create an instance of OSWConfidenceMetric
        zip_path = '/src/downloads/valid.zip'  # Provide the correct path
        metric = OSWConfidenceMetric(zip_file=zip_path)

        # Calculate the score using calculate_score method
        score = metric.calculate_score()

        # Use the obtained score in your function
        print('Score from OSWConfidenceMetric:', score)


# Usage
if __name__ == '__main__':
    different_instance = DifferentClass()
    different_instance.my_function()