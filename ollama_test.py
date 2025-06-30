from pipeline import classify_transcript, labels_to_csv
import config

if __name__ == "__main__":
    labeled_json = classify_transcript(
        transcript_path=config.CLEAN_TRANSCRIPT,
        output_path=config.LABELED_TRANSCRIPT,
    )
    labels_to_csv(labeled_json, config.CSV_PATH)
