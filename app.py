from flask import Flask, request, jsonify, send_file
import os
import traceback
from pathlib import Path  # Import Path from pathlib module

# Assuming these functions are defined in your script
from src.spotify_dl import get_track_data, _get_track_local_title, download_track

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download_track_route():
    try:
        track_id = request.args.get('track_id')
        if not track_id:
            return jsonify({"error": "track_id is required"}), 400

        # Fetch track data using the given track_id
        track_resp_json = get_track_data(track_id=track_id)
        if not track_resp_json:
            return jsonify({"error": "Song not found"}), 404
        
        # Extract and format the track title
        track_title = _get_track_local_title(track_resp_json['metadata']['title'], track_resp_json['metadata']['artists'])
        
        # Define output directory (you can customize this as needed)
        output_dir = 'downloads'
        dest_dir = Path(output_dir)  # Convert output_dir to a Path object
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True)

        # Download the track and get binary data and filename
        binary_data, filename, filepath = download_track(track_id, track_title, dest_dir, interactive=False)

        if binary_data is None:
            return jsonify({"message": f"Track '{track_title}' already exists"}), 200

        # Return the binary data as a file attachment
        return send_file(
            filepath,
            mimetype='audio/mpeg',
            as_attachment=True,
        )

    except Exception as exc:
        if app.debug:
            return jsonify({"error": str(exc), "traceback": traceback.format_exc()}), 500
        return jsonify({"error": "An error occurred"}), 500


if __name__ == '__main__':
    app.run(debug=True)
