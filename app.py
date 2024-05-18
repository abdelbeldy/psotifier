from flask import Flask, request, jsonify, send_file
import os
import traceback
from pathlib import Path

from src.spotify_dl import get_track_data, _get_track_local_title, download_track

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download_track_route():
    try:
        track_id = request.args.get('track_id')
        if not track_id:
            return jsonify({"error": "track_id is required"}), 400

        track_resp_json = get_track_data(track_id=track_id)
        if not track_resp_json:
            return jsonify({"error": "Song not found"}), 404
        
        track_title = _get_track_local_title(track_resp_json['metadata']['title'], track_resp_json['metadata']['artists'])
        
        output_dir = 'downloads'
        dest_dir = Path(output_dir)
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True)

        # Download the track and get binary data and filename
        binary_data, filename, filepath = download_track(track_id, track_title, dest_dir, interactive=False)

        if binary_data is None:
            # If the binary_data is None, it means the track already exists, so return a success message
            return jsonify({"message": f"Track '{track_title}' already exists"}), 200

        # Return the binary data as a file attachment
        response = send_file(
            filepath,
            mimetype='audio/mpeg',
            as_attachment=True,
        )

        # After sending the file, delete it
        if os.path.exists(filepath):
            os.remove(filepath)

        return response

    except Exception as exc:
        if app.debug:
            return jsonify({"error": str(exc), "traceback": traceback.format_exc()}), 500
        return jsonify({"error": "An error occurred"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
