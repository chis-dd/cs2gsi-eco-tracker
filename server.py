from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)

team_data = {
    'CT': {'score': 0, 'consecutive_round_losses': 0, 'last_score': 0, 'estimate_eco': 0, 'total_income': 0, 'timeline': [] },
    'T': {'score': 0, 'consecutive_round_losses': 0, 'last_score': 0, 'estimate_eco': 0, 'total_income': 0, 'timeline': [] }
}

bomb_planted = False
cr = 0

@app.route('/update')
def update_dashboard():
    global team_data
    return jsonify(team_data)

@app.route('/reset')
def reset_data():
    global team_data

    team_data = {
    'CT': {'score': 0, 'consecutive_round_losses': 0, 'last_score': 0, 'estimate_eco': 0, 'total_income': 0, 'timeline': [] },
    'T': {'score': 0, 'consecutive_round_losses': 0, 'last_score': 0, 'estimate_eco': 0, 'total_income': 0, 'timeline': [] }
    }

    return redirect(url_for('index'))

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        global team_data
        global bomb_planted
        global cr

        game_data = request.json

        # print(game_data)
        if 'map' in game_data and game_data['map'] is not None:
            # print(game_data)

            if 'round' in game_data and 'bomb' in game_data['round'] and game_data['round']['bomb'] == 'planted':
                # print('bomb planted')
                bomb_planted = True
            

            if 'round' in game_data and 'phase' in game_data['round'] and game_data['round']['phase'] == 'freezetime':
                # if team_data['CT']['score'] != game_data['map']['team_ct']['score'] or team_data['T']['score'] != game_data['map']['team_t']['score']:
                
                current_round = game_data['map']['round']
                if cr == current_round:
                    if current_round == 0:
                        team_data = {
                            'CT': {'score': 0, 'consecutive_round_losses': 0, 'last_score': 0, 'estimate_eco': 0, 'total_income': 0, 'timeline': [] },
                            'T': {'score': 0, 'consecutive_round_losses': 0, 'last_score': 0, 'estimate_eco': 0, 'total_income': 0, 'timeline': [] }
                        }

                    # Update team data from the incoming JSON payload
                    ct_score = game_data['map']['team_ct']['score']
                    ct_consecutive_losses = game_data['map']['team_ct']['consecutive_round_losses']
                    t_score = game_data['map']['team_t']['score']
                    t_consecutive_losses = game_data['map']['team_t']['consecutive_round_losses']

                    # Determine which team won the last round
                    ct_winner = False
                    t_winner = False
                    if ct_score > team_data['CT']['score']:
                        ct_winner = True
                    elif t_score > team_data['T']['score']:
                        t_winner = True

                    # Calculate estimated economy for each team (simplified calculation)
                    ct_income = calculate_economy_estimate(ct_score, ct_consecutive_losses, ct_winner)
                    t_income = calculate_economy_estimate(t_score, t_consecutive_losses, t_winner)

                    # Return the estimated economy for each team
                    team_data['CT'] = {
                        'score': ct_score,
                        'consecutive_round_losses': ct_consecutive_losses,
                        'estimate_eco': ct_income,
                        'total_income': team_data['CT']['total_income'] + ct_income,
                        'timeline' : team_data['CT']['timeline']
                    }

                    team_data['T'] = {
                        'score': t_score,
                        'consecutive_round_losses': t_consecutive_losses,
                        'estimate_eco': t_income,
                        'total_income': team_data['T']['total_income'] + t_income,
                        'timeline' : team_data['T']['timeline']
                    }

                    if ct_winner:
                        team_data['CT']['timeline'].append({'round': current_round, 'income': ct_income})
                        team_data['T']['timeline'].append({'round': current_round, 'income': t_income})
                    elif t_winner:
                        team_data['T']['timeline'].append({'round': current_round, 'income': t_income})
                        team_data['CT']['timeline'].append({'round': current_round, 'income': ct_income})

                    print(team_data)

                    if current_round == 12:
                        team_data = {
                            'CT': {'score': 0, 'consecutive_round_losses': 0, 'last_score': 0, 'estimate_eco': 800, 'total_income': 0, 'timeline': [] },
                            'T': {'score': 0, 'consecutive_round_losses': 0, 'last_score': 0, 'estimate_eco': 800, 'total_income': 0, 'timeline': [] }
                        }

                    print(current_round)
                    cr += 1

                    return ''
                else: 
                    return ''
            else:
                return ''
        else:
            # team_data = {
            #     'CT': {'score': 0, 'consecutive_round_losses': 0, 'last_score': 0, 'estimate_eco': 0, 'total_income': 0, 'timeline': [] },
            #     'T': {'score': 0, 'consecutive_round_losses': 0, 'last_score': 0, 'estimate_eco': 0, 'total_income': 0, 'timeline': [] }
            #     }
            print('waiting for game to start')
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
        return 3500 + (crl * 500)
    
    if winner and not bomb_planted:
        return 3250 + (crl * 500)
    else :
        return (crl * 500) + 1400

if __name__ == '__main__':
    app.run(debug=True)
