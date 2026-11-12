# 1. Run the script to populate agency_sentience.db and enlightenment_corpus.json
python3 ingest_enlightenment_media.py

# 2. Stage, commit, and push the new script to your repository
git add ingest_enlightenment_media.py enlightenment_corpus.json
git commit -m "Add experiential wisdom corpus script for consciousness and purpose"
git push origin main
