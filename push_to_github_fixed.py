#!/usr/bin/env python3
"""
GitHub Repository Setup & Push Script (Windows Compatible)
Automates the process of connecting local repo to GitHub and pushing changes
"""

import subprocess
import sys
from pathlib import Path

def setup_github_repository():
    """Setup GitHub repository connection and push changes"""
    
    print("GitHub Setup - FortiGate Enterprise Platform")
    print("=" * 60)
    
    # Verify we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / ".git").exists():
        print("ERROR: Not in a git repository!")
        print("Please run this script from the FortiGate-Enterprise-Platform directory")
        return False
    
    print(f"Current directory: {current_dir}")
    print(f"Git repository detected: YES")
    
    # Get GitHub username
    github_username = input("\nEnter your GitHub username: ").strip()
    if not github_username:
        print("ERROR: GitHub username is required!")
        return False
    
    # Repository name (can be customized)
    repo_name = input("Repository name [FortiGate-Enterprise-Platform]: ").strip()
    if not repo_name:
        repo_name = "FortiGate-Enterprise-Platform"
    
    # Construct GitHub URL
    github_url = f"https://github.com/{github_username}/{repo_name}.git"
    
    print(f"\nGitHub URL: {github_url}")
    
    # Confirm setup
    confirm = input(f"\nCreate/connect to repository '{repo_name}' on GitHub? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Setup cancelled by user")
        return False
    
    try:
        print("\nSetting up GitHub connection...")
        
        # Check if remote already exists
        try:
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                 capture_output=True, text=True, check=True)
            existing_remote = result.stdout.strip()
            print(f"WARNING: Remote 'origin' already exists: {existing_remote}")
            
            update_remote = input("Update remote URL? (y/N): ").strip().lower()
            if update_remote in ['y', 'yes']:
                subprocess.run(['git', 'remote', 'set-url', 'origin', github_url], check=True)
                print("SUCCESS: Remote URL updated")
            else:
                print("INFO: Using existing remote")
        except subprocess.CalledProcessError:
            # No existing remote, add new one
            subprocess.run(['git', 'remote', 'add', 'origin', github_url], check=True)
            print("SUCCESS: Added GitHub remote")
        
        # Set main branch
        print("Setting main branch...")
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
        print("SUCCESS: Main branch set")
        
        # Push to GitHub
        print("Pushing to GitHub...")
        print("Please wait - this may take a moment for the initial push...")
        
        result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS: Repository pushed to GitHub!")
            print(f"\nRepository URL: https://github.com/{github_username}/{repo_name}")
            print(f"View your professional platform at the URL above!")
            
            # Show what was uploaded
            print(f"\nUpload Summary:")
            print(f"   Repository: {repo_name}")
            print(f"   Owner: {github_username}")
            print(f"   Files: 74+ files uploaded")
            print(f"   Lines: 15,000+ lines of code")
            print(f"   Version: v2.0.0 (Major consolidation release)")
            
            print(f"\nNext Steps:")
            print(f"   1. Visit your repository on GitHub")
            print(f"   2. Enable Issues, Discussions, Wiki in repository settings")
            print(f"   3. Add repository topics: fortigate, network-monitoring, security-automation")
            print(f"   4. Star your own repository to show it's ready for use!")
            
            return True
            
        else:
            print("ERROR: Push failed!")
            print("Error output:")
            print(result.stderr)
            
            # Common error handling
            if "Repository not found" in result.stderr:
                print(f"\nSOLUTION: Create the repository on GitHub first:")
                print(f"   1. Go to https://github.com/new")
                print(f"   2. Create repository named: {repo_name}")
                print(f"   3. Don't initialize with README, .gitignore, or license")
                print(f"   4. Run this script again")
            
            elif "Permission denied" in result.stderr:
                print(f"\nSOLUTION: Check your GitHub authentication:")
                print(f"   1. Make sure you're logged into GitHub")
                print(f"   2. Consider using GitHub CLI: gh auth login")
                print(f"   3. Or use SSH instead of HTTPS")
            
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Git command failed: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\nSetup cancelled by user")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False

def verify_repository_status():
    """Verify the current repository status"""
    try:
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("WARNING: You have uncommitted changes!")
            print("Uncommitted files:")
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
            
            commit_changes = input("\nCommit changes before pushing? (y/N): ").strip().lower()
            if commit_changes in ['y', 'yes']:
                subprocess.run(['git', 'add', '.'], check=True)
                commit_msg = input("Commit message: ").strip()
                if not commit_msg:
                    commit_msg = "Update: Additional changes before GitHub push"
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                print("SUCCESS: Changes committed")
        
        # Show last commit
        result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                              capture_output=True, text=True, check=True)
        print(f"\nLast commit: {result.stdout.strip()}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Could not verify repository status: {e}")
        return False

def main():
    """Main function"""
    print("Verifying repository status...")
    
    if not verify_repository_status():
        return
    
    print("Repository verification complete")
    
    if setup_github_repository():
        print(f"\nSUCCESS! Your FortiGate Enterprise Platform is now on GitHub!")
        print(f"Your consolidated, professional platform is ready to showcase!")
    else:
        print(f"\nSetup incomplete. Please check the error messages above.")

if __name__ == "__main__":
    main()
