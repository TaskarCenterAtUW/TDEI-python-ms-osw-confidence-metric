import json
scores = json.loads('{"type": "FeatureCollection", "features": [{"id": "0", "type": "Feature", "properties": {"confidence_score": 0.75}, "geometry": {"type": "Polygon", "coordinates": [[[-122.1322201, 47.63528], [-122.1378655, 47.6353141], [-122.1395176, 47.6355614], [-122.1431969, 47.6365115], [-122.1443805, 47.6385402], [-122.1469453, 47.6460242], [-122.1429792, 47.6495373], [-122.1403351, 47.6497278], [-122.1325839, 47.6498422],  [-122.1321999, 47.6496722], [-122.1321845, 47.6496558], [-122.1285859, 47.6378078], [-122.1322201, 47.63528]]]}}]}'),
print(scores)