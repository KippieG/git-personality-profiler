import subprocess
import datetime
import collections
import sys
import os
import math

# Kleuren voor de terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def run_git_command(command, path="."):
    try:
        result = subprocess.check_output(command, shell=True, cwd=path, stderr=subprocess.STDOUT)
        return result.decode('utf-8', errors='ignore')
    except subprocess.CalledProcessError:
        return None

def analyze_git_history(path="."):
    # at: timestamp, s: subject, an: author, b: body, n: numstat (handled separately)
    log_format = "%at|%s"
    output = run_git_command(f'git log --pretty=format:"{log_format}" --shortstat', path)
    
    if not output:
        print(f"{Colors.FAIL}❌ Geen Git geschiedenis gevonden in {path}.{Colors.ENDC}")
        return None

    commits = []
    lines = output.split('\n')
    current_commit = None
    
    for line in lines:
        if not line.strip(): continue
        
        if '|' in line and not line.startswith(' '):
            if current_commit: commits.append(current_commit)
            ts, msg = line.split('|', 1)
            current_commit = {
                'time': datetime.datetime.fromtimestamp(int(ts)),
                'message': msg.lower(),
                'changes': 0,
                'insertions': 0,
                'deletions': 0
            }
        elif 'file' in line and ('changed' in line or 'insertion' in line):
            # Parse shortstat: " 2 files changed, 10 insertions(+), 5 deletions(-)"
            parts = line.strip().split(',')
            for part in parts:
                if 'insertion' in part:
                    current_commit['insertions'] = int(part.strip().split(' ')[0])
                if 'deletion' in part:
                    current_commit['deletions'] = int(part.strip().split(' ')[0])
            current_commit['changes'] = current_commit['insertions'] + current_commit['deletions']

    if current_commit: commits.append(current_commit)
    return commits

def get_profile(commits):
    total = len(commits)
    if total == 0: return None

    # Time-based metrics
    hours = [c['time'].hour for c in commits]
    days = [c['time'].strftime('%A') for c in commits]
    day_counts = collections.Counter(days)
    
    # Archetype scores
    midnight_score = (len([h for h in hours if 0 <= h <= 5]) / total) * 100
    morning_score = (len([h for h in hours if 6 <= h <= 10]) / total) * 100
    weekend_score = (len([d for d in days if d in ['Saturday', 'Sunday']]) / total) * 100

    # Impact and Style
    total_insertions = sum(c['insertions'] for c in commits)
    total_deletions = sum(c['deletions'] for c in commits)
    avg_impact = sum(c['changes'] for c in commits) / total
    
    # Personality Heuristics
    perfectionist_keywords = ['refactor', 'fix', 'clean', 'style', 'lint', 'improve', 'optimize', 'polish']
    perf_count = len([c for c in commits if any(k in c['message'] for k in perfectionist_keywords)])
    perfectionist_score = (perf_count / total) * 100

    chaos_keywords = ['oops', 'test', '.', 'asdf', 'fixed', 'wip', 'save', 'commit']
    chaos_count = len([c for c in commits if any(k == c['message'].strip() for k in chaos_keywords) or len(c['message']) < 6])
    chaos_score = (chaos_count / total) * 100

    # Emotional state (Heuristic based on message content)
    angry_keywords = ['hate', 'stupid', 'dumb', 'fix this', '!!', '???', 'wtf', 'damn']
    angry_count = len([c for c in commits if any(k in c['message'] for k in angry_keywords)])
    angry_score = (angry_count / total) * 100

    return {
        'total': total,
        'midnight': midnight_score,
        'morning': morning_score,
        'weekend': weekend_score,
        'perfectionist': perfectionist_score,
        'chaos': chaos_score,
        'angry': angry_score,
        'avg_impact': avg_impact,
        'total_ins': total_insertions,
        'total_del': total_deletions,
        'best_day': day_counts.most_common(1)[0] if day_counts else ("None", 0),
        'avg_msg_len': sum(len(c['message']) for c in commits) / total
    }

def draw_bar(label, percentage, color):
    width = 20
    filled = int(percentage / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    print(f"{label:<15} {color}[{bar}] {percentage:>5.1f}%{Colors.ENDC}")

def print_dashboard(profile):
    print("\n" + Colors.BOLD + Colors.HEADER + "┏" + "━"*50 + "┓" + Colors.ENDC)
    print(Colors.BOLD + Colors.HEADER + "┃" + " "*13 + "🧠 GIT PERSONALITY PROFILER 2.0" + " "*12 + "┃" + Colors.ENDC)
    print(Colors.BOLD + Colors.HEADER + "┗" + "━"*50 + "┛" + Colors.ENDC)
    
    print(f"\n{Colors.BOLD}📊 STATISTIEKEN{Colors.ENDC}")
    print(f"  Commits: {Colors.CYAN}{profile['total']}{Colors.ENDC}")
    print(f"  Impact:  {Colors.GREEN}+{profile['total_ins']}{Colors.ENDC} / {Colors.FAIL}-{profile['total_del']}{Colors.ENDC} regels")
    print(f"  Favoriete dag: {Colors.WARNING}{profile['best_day'][0]}{Colors.ENDC} ({profile['best_day'][1]} commits)")
    
    print(f"\n{Colors.BOLD}🧬 DNA PROFIEL{Colors.ENDC}")
    draw_bar("Nachtuil 🧛", profile['midnight'], Colors.BLUE)
    draw_bar("Vroege Vogel 🐦", profile['morning'], Colors.CYAN)
    draw_bar("Weekend Warrior ⚔️", profile['weekend'], Colors.WARNING)
    draw_bar("Perfectionist ✨", profile['perfectionist'], Colors.GREEN)
    draw_bar("Chaos Aap 🐒", profile['chaos'], Colors.FAIL)
    draw_bar("Gemoedstoestand 💢", profile['angry'], Colors.FAIL)

    # Determine Archetype
    archetype = "The Professional"
    desc = "Degelijk en voorspelbaar. De ruggengraat van elk project."
    
    if profile['midnight'] > 25:
        archetype = "The Midnight Shadow 🧛"
        desc = "Leeft op cafeïne en codeert als de rest van de wereld slaapt."
    elif profile['chaos'] > 40:
        archetype = "The Chaos Engineer 🐒"
        desc = "Schrijft code sneller dan zijn eigen schaduw. 'Commit now, fix never'."
    elif profile['perfectionist'] > 30:
        archetype = "The Architect ✨"
        desc = "Elke punt en komma moet perfect staan. Refactoren is een levensstijl."
    elif profile['angry'] > 10:
        archetype = "The Grumpy Dev 💢"
        desc = "Heeft een haat-liefdeverhouding met de codebase. Vooral haat."
    elif profile['avg_impact'] > 500:
        archetype = "The Tank 🧱"
        desc = "Maakt zelden commits, maar als ze komen zijn ze ENORM."
    elif profile['weekend'] > 40:
        archetype = "The Passionate Coder ⚔️"
        desc = "Maakt van zijn hobby zijn werk, zelfs op zondagmiddag."

    print(f"\n{Colors.BOLD}🏆 UW ARCHETYPE:{Colors.ENDC}")
    print(f"  {Colors.BOLD}{Colors.GREEN}{archetype}{Colors.ENDC}")
    print(f"  {Colors.BLUE}\"{desc}\"{Colors.ENDC}")
    print("\n" + Colors.HEADER + "━"*52 + Colors.ENDC + "\n")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    commits = analyze_git_history(path)
    if commits:
        profile = get_profile(commits)
        print_dashboard(profile)
