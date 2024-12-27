from flask import Flask, jsonify, request
from pymongo import MongoClient

# Initialize Flask app
app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"  # Replace with your MongoDB URI
client = MongoClient(MONGO_URI)
db = client['snmp_database']  # Database name
collection = db['snmp_traps']  # Collection name



# Route to get all traps
@app.route('/api/snmp_traps', methods=['GET'])
def get_snmp_traps():
    traps = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB's _id field
    return jsonify(traps)




# Route to get a particular trap by ID
@app.route('/api/snmp_traps/<int:trap_id>', methods=['GET'])
def get_snmp_trap(trap_id):
    trap = collection.find_one({'id': trap_id}, {'_id': 0})
    if trap:
        return jsonify(trap)
    else:
        return jsonify({"message": "Trap not found"}), 404


# Route to create a new SNMP trap
@app.route('/api/snmp_traps', methods=['POST'])
def create_snmp_trap():

    try:
        # Parse the incoming JSON data

        new_trap = request.get_json()


        # Ensure the data is valid
        if not new_trap:
            return jsonify({"error": "No data provided"}), 400

        # Insert the data into MongoDB
        result = collection.insert_one(new_trap)

        return jsonify({
            "message": "Document added successfully",
            "inserted_id": str(result.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to update a SNMP trap by ID
@app.route('/api/snmp_traps', methods=['PUT'])
def update_document():
    try:
        # Parse the request body for filter and update data
        data = request.get_json()

        # Ensure the filter and update fields are provided
        if not data or 'filter' not in data or 'update' not in data:
            return jsonify({"error": "Request body must contain 'filter' and 'update' fields"}), 400

        filter_data = data['filter']  # Filter to match documents
        update_data = {"$set": data['update']}  # Update data

        # Update matching documents
        result = collection.update_many(filter_data, update_data)

        # Return the result
        if result.modified_count > 0:
            return jsonify({
                "message": f"{result.modified_count} document(s) updated successfully"
            }), 200
        else:
            return jsonify({"message": "No documents matched the filter or no changes made"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to delete a SNMP trap by ID
#


# Route to filter traps based on TrapType or AgentAddress
@app.route('/api/snmp_traps/filter', methods=['GET'])
def filter_snmp_traps():
    trap_type = request.args.get('TrapType')
    agent_address = request.args.get('AgentAddress')

    query = {}
    if trap_type:
        query['TrapType'] = trap_type
    if agent_address:
        query['AgentAddress'] = agent_address

    filtered_traps = list(collection.find(query, {'_id': 0}))
    if filtered_traps:
        return jsonify({"SNMPTraps": filtered_traps})
    else:
        return jsonify({"message": "No matching traps found"}), 404

@app.route('/api/snmp_traps', methods=['DELETE'])
def delete_document():
    try:
        # Parse the JSON filter from the request body
        filter_data = request.get_json()

        # Ensure filter data is provided
        if not filter_data:
            return jsonify({"error": "No filter provided"}), 400

        # Delete matching documents
        result = collection.delete_many(filter_data)

        # Return the result
        if result.deleted_count > 0:
            return jsonify({
                "message": f"{result.deleted_count} document(s) deleted successfully"
            }), 200
        else:
            return jsonify({"message": "No documents matched the filter"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=8000)
