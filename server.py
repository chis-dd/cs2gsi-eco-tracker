from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

team_data = {
    'CT': {'score': 0, 'consecutive_round_losses': 0, 'last_score' : 0, 'estimate_eco' : 0},
    'T': {'score': 0, 'consecutive_round_losses': 0, 'last_score' : 0, 'estimate_eco' : 0}
}
bomb_planted = False

@app.route('/update')
def update_dashboard():
    global team_data
    return jsonify(team_data)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        global team_data
        global bomb_planted

        game_data = request.json


        if 'map' in game_data and game_data['map'] is not None:
            # print(game_data)

            if 'round' in game_data and 'bomb' in game_data['round'] and game_data['round']['bomb'] == 'planted':
                # print('bomb planted')
                bomb_planted = True
            

            if 'round' in game_data and game_data['round']['phase'] == 'freezetime':
                if team_data['CT']['score'] != game_data['map']['team_ct']['score'] or team_data['T']['score'] != game_data['map']['team_t']['score']:

                    # Update team data from the incoming JSON payload
                    ct_score = game_data['map']['team_ct']['score']
                    ct_consecutive_losses = game_data['map']['team_ct']['consecutive_round_losses']
                    t_score = game_data['map']['team_t']['score']
                    t_consecutive_losses = game_data['map']['team_t']['consecutive_round_losses']

                    # Determine which team won the last round
                    # Determine which team won the last round
                    ct_winner = False
                    t_winner = False
                    if ct_score > team_data['CT']['score']:
                        ct_winner = True
                    elif t_score > team_data['T']['score']:
                        t_winner = True

                    # Calculate estimated economy for each team (simplified calculation)
                    ct_economy = calculate_economy_estimate(ct_score, ct_consecutive_losses, ct_winner)
                    t_economy = calculate_economy_estimate(t_score, t_consecutive_losses, t_winner)

                    # Return the estimated economy for each team
                    team_data['CT'] = {
                        'score': ct_score,
                        'consecutive_round_losses': ct_consecutive_losses,
                        'estimate_eco': ct_economy,
                    }
                    team_data['T'] = {
                        'score': t_score,
                        'consecutive_round_losses': t_consecutive_losses,
                        'estimate_eco': t_economy,
                    }
                    # print(ct_economy, t_economy)
                    return ''
                else: 
                    return ''
            else:
                return ''
        else:
            return ''
    else:
        return render_template('dashboard.html')

def calculate_economy_estimate(score, consecutive_round_losses, winner):
    global bomb_planted
    if score == 0 and consecutive_round_losses == 1:
        return 800

    crl = consecutive_round_losses - 1
    
    if crl < 0 :
        crl = 0
    elif crl > 4:
        crl = 4

    if winner and bomb_planted:
        bomb_planted = False
        test = (crl * 500)
        print(test)
        return 3500 + (crl * 500)
    
    if winner and not bomb_planted:
        # print(crl)
        return 3250 + (crl * 500)
    else :
        print(consecutive_round_losses)
        return (crl * 500) + 1400

if __name__ == '__main__':
    app.run(debug=True)
