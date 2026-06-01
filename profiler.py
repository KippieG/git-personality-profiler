import subprocess
import datetime
import collections
import sys
import os
import math

# Kleuren en UI Elementen
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
    MAGENTA = '\033[35m'

DNA_HELIX = [
    "  {c}GC{e}      ",
    " {c}G{e}──{c}C{e}     ",
    "{c}A{e}────{c}T{e}    ",
    " {c}T{e}──{c}A{e}     ",
    "  {c}CG{e}      ",
    " {c}T{e}──{c}A{e}     ",
    "{c}G{e}────{c}C{e}    ",
    " {c}A{e}──{c}T{e}     "
]

def run_git_command(command, path="."):
    try:
        result = subprocess.check_output(command, shell=True, cwd=path, stderr=subprocess.STDOUT)
        return result.decode('utf-8', errors='ignore')
    except subprocess.CalledProcessError:
        return None

def analyze_git_history(path="."):
    # at: timestamp, s: subject, an: author
    log_format = "%at|%s"
    output = run_git_command(f'git log --pretty=format:"{log_format}" --shortstat --name-only', path)
    
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
                'changes': 0, 'insertions': 0, 'deletions': 0,
                'files': []
            }
        elif 'file' in line and ('changed' in line or 'insertion' in line):
            parts = line.strip().split(',')
            for part in parts:
                if 'insertion' in part:
                    current_commit['insertions'] = int(part.strip().split(' ')[0])
                if 'deletion' in part:
                    current_commit['deletions'] = int(part.strip().split(' ')[0])
            current_commit['changes'] = current_commit['insertions'] + current_commit['deletions']
        elif '.' in line: # Likely a file path
            current_commit['files'].append(line.strip())

    if current_commit: commits.append(current_commit)
    return commits

def get_tech_stack(commits):
    extensions = []
    for c in commits:
        for f in c['files']:
            ext = os.path.splitext(f)[1].lower()
            if ext: extensions.append(ext)
    
    mapping = {
        '.py': 'Python 🐍', '.js': 'JavaScript 🟨', '.ts': 'TypeScript 🟦',
        '.java': 'Java ☕', '.cpp': 'C++ ⚙️', '.c': 'C 🔧',
        '.html': 'HTML 🌐', '.css': 'CSS 🎨', '.md': 'Markdown 📝',
        '.go': 'Go 🐹', '.rs': 'Rust 🦀', '.php': 'PHP 🐘',
        '.rb': 'Ruby 💎', '.swift': 'Swift 🍎', '.kt': 'Kotlin 🤖'
    }
    
    counts = collections.Counter([mapping.get(ext, ext) for ext in extensions])
    return counts.most_common(3)

def get_profile(commits):
    total = len(commits)
    if total == 0: return None

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
    perfectionist_keywords = ['refactor', 'fix', 'clean', 'style', 'lint', 'improve', 'optimize', 'polish', 'reformat']
    perf_count = len([c for c in commits if any(k in c['message'] for k in perfectionist_keywords)])
    perfectionist_score = (perf_count / total) * 100

    chaos_keywords = ['oops', 'test', '.', 'asdf', 'fixed', 'wip', 'save', 'commit', 'update']
    chaos_count = len([c for c in commits if any(k == c['message'].strip() for k in chaos_keywords) or len(c['message']) < 6])
    chaos_score = (chaos_count / total) * 100

    angry_keywords = ['hate', 'stupid', 'dumb', 'fix this', '!!', '???', 'wtf', 'damn', 'fuck', 'shit']
    angry_count = len([c for c in commits if any(k in c['message'] for k in angry_keywords)])
    angry_score = (angry_count / total) * 100

    # Streak analysis
    dates = sorted(list(set([c['time'].date() for c in commits])))
    max_streak = 0
    current_streak = 0
    if dates:
        current_streak = 1
        max_streak = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1

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
        'avg_msg_len': sum(len(c['message']) for c in commits) / total,
        'tech_stack': get_tech_stack(commits),
        'streak': max_streak
    }

def draw_dna():
    colors = [Colors.CYAN, Colors.MAGENTA, Colors.BLUE, Colors.GREEN]
    for i, line in enumerate(DNA_HELIX):
        color = colors[i % len(colors)]
        print("      " + line.format(c=color, e=Colors.ENDC))

def print_dashboard(profile):
    print("\n" + Colors.BOLD + Colors.CYAN + "╔" + "═"*60 + "╗" + Colors.ENDC)
    print(Colors.BOLD + Colors.CYAN + "║" + " "*17 + "🧬 GIT PERSONALITY PROFILER v3.0" + " "*11 + "║" + Colors.ENDC)
    print(Colors.BOLD + Colors.CYAN + "╚" + "═"*60 + "╝" + Colors.ENDC)
    
    draw_dna()

    print(f"\n{Colors.BOLD}🚀 TECH STACK (Top Languages){Colors.ENDC}")
    for lang, count in profile['tech_stack']:
        print(f"  • {lang:<15} ({count} files changed)")

    print(f"\n{Colors.BOLD}📊 DEEP SCAN STATS{Colors.ENDC}")
    col1 = f"  Commits: {Colors.CYAN}{profile['total']}{Colors.ENDC}"
    col2 = f"Impact: {Colors.GREEN}+{profile['total_ins']}{Colors.ENDC} / {Colors.FAIL}-{profile['total_del']}{Colors.ENDC}"
    print(f"{col1:<35} {col2}")
    
    col3 = f"  Streak:  {Colors.MAGENTA}{profile['streak']} dagen{Colors.ENDC}"
    col4 = f"Fav Day: {Colors.WARNING}{profile['best_day'][0]}{Colors.ENDC}"
    print(f"{col3:<35} {col4}")

    print(f"\n{Colors.BOLD}🧬 DEVELOPER DNA{Colors.ENDC}")
    def draw_bar(label, percentage, color):
        width = 25
        filled = int(percentage / 100 * width)
        bar = "█" * filled + "░" * (width - filled)
        print(f"  {label:<18} {color}[{bar}] {percentage:>5.1f}%{Colors.ENDC}")

    draw_bar("Night Owl 🧛", profile['midnight'], Colors.BLUE)
    draw_bar("Early Bird 🐦", profile['morning'], Colors.CYAN)
    draw_bar("Weekend Warrior ⚔️", profile['weekend'], Colors.WARNING)
    draw_bar("Clean Coder ✨", profile['perfectionist'], Colors.GREEN)
    draw_bar("Chaos Factor 🐒", profile['chaos'], Colors.FAIL)
    draw_bar("Saltiness 💢", profile['angry'], Colors.FAIL)

    # Archetype Logic
    archetype, desc, advice = "The Professional", "Stable and reliable.", "Keep up the steady pace!"
    
    if profile['midnight'] > 30:
        archetype, desc = "The Midnight Shadow 🧛", "Fueled by caffeine and dark mode."
        advice = "Try seeing the sun once in a while. Vitamin D is important!"
    elif profile['chaos'] > 45:
        archetype, desc = "The Chaos Engineer 🐒", "Speed is everything. Documentation is for the weak."
        advice = "Maybe try a commit message longer than 4 characters? Your future self will thank you."
    elif profile['perfectionist'] > 35:
        archetype, desc = "The Architect ✨", "Code is art. Every line must be a masterpiece."
        advice = "Don't let perfect be the enemy of done. Ship it!"
    elif profile['angry'] > 15:
        archetype, desc = "The Salty Senior 💢", "The codebase is a minefield, and you're the bomb squad."
        advice = "Take a deep breath. It's just code. Maybe go for a walk?"
    elif profile['avg_impact'] > 800:
        archetype, desc = "The Juggernaut 🧱", "When you push, the CI/CD server trembles."
        advice = "Smaller commits are easier to review. Try breaking down your tasks!"
    elif profile['streak'] > 10:
        archetype, desc = "The Code Machine 🤖", "Committing every single day. Unstoppable."
        advice = "A day off won't kill you. Rest is part of the work!"

    print(f"\n{Colors.BOLD}🏆 YOUR ARCHETYPE:{Colors.ENDC}")
    print(f"  {Colors.BOLD}{Colors.GREEN}{archetype}{Colors.ENDC}")
    print(f"  {Colors.BLUE}\"{desc}\"{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}💡 PERSONAL ADVICE:{Colors.ENDC}")
    print(f"  {Colors.WARNING}{advice}{Colors.ENDC}")
    
    print("\n" + Colors.CYAN + "═"*62 + Colors.ENDC + "\n")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    commits = analyze_git_history(path)
    if commits:
        profile = get_profile(commits)
        print_dashboard(profile)
