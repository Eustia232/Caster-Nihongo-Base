import subprocess
import os
import time
from datetime import datetime
from src.core.exceptions import SyncError

# Bot environment variables to maintain clean history
BOT_ENV = os.environ.copy()
BOT_ENV["GIT_AUTHOR_NAME"] = "Caster Auto Sync"
BOT_ENV["GIT_AUTHOR_EMAIL"] = "caster@nihongo.local"
BOT_ENV["GIT_COMMITTER_NAME"] = "Caster Auto Sync"
BOT_ENV["GIT_COMMITTER_EMAIL"] = "caster@nihongo.local"


def check_git_env() -> None:
    """Check if Git is installed and if the current branch has an upstream."""
    try:
        subprocess.run(
            ["git", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise SyncError("系统未安装 Git，或 Git 命令未添加到环境变量中。")

    try:
        # Check if upstream is set
        subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError:
        raise SyncError(
            "当前分支未绑定远程分支 (Upstream)。请手动执行一次 `git push --set-upstream origin <当前分支名>`。"
        )


def sync_pull(data_dir: str) -> None:
    """Pull changes from the remote repository."""
    try:
        result = subprocess.run(
            ["git", "pull", "--rebase"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            output = result.stdout + result.stderr
            if (
                "unstaged changes" in output
                or "not up to date" in output
                or "Please commit your changes" in output
                or "overwritten by merge" in output
            ):
                raise SyncError(
                    "本地工作区存在未提交的修改，Git 拒绝拉取云端数据，请先 Commit 或 Stash 您的代码改动。"
                )
            if "CONFLICT" in output or "conflict" in output.lower():
                subprocess.run(["git", "rebase", "--abort"], capture_output=True)
                raise SyncError("检测到云端与本地进度存在冲突，请手动解决。")
            raise SyncError(f"拉取云端数据失败: {output.strip()}")
    except subprocess.TimeoutExpired:
        raise SyncError("拉取云端数据超时 (15秒)，请检查网络连接。")
    except subprocess.CalledProcessError as e:
        output = e.stdout + e.stderr
        if (
            "unstaged changes" in output
            or "not up to date" in output
            or "Please commit your changes" in output
            or "overwritten by merge" in output
        ):
            raise SyncError(
                "本地工作区存在未提交的修改，Git 拒绝拉取云端数据，请先 Commit 或 Stash 您的代码改动。"
            )
        if "CONFLICT" in output or "conflict" in output.lower():
            subprocess.run(["git", "rebase", "--abort"], capture_output=True)
            raise SyncError("检测到云端与本地进度存在冲突，请手动解决。")
        raise SyncError(f"拉取云端数据失败: {output.strip()}")


def sync_push(data_dir: str) -> None:
    """Commit and push changes in the data_dir to the remote repository."""
    # Ensure data_dir path is properly formatted for Git
    git_add_path = os.path.normpath(data_dir).replace("\\", "/")

    # Add files in data directory
    try:
        subprocess.run(
            ["git", "add", git_add_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise SyncError(
            f"无法添加数据到暂存区: {e.stderr.decode('utf-8', errors='replace').strip()}"
        )

    # Check if there are changes to commit
    diff_result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if diff_result.returncode == 0:
        # No changes
        return

    # Commit changes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"chore(data): auto sync data_store [{timestamp}]"

    try:
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            env=BOT_ENV,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise SyncError(
            f"提交数据失败: {e.stderr.decode('utf-8', errors='replace').strip()}"
        )

    # Push to remote
    try:
        subprocess.run(
            ["git", "push"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        raise SyncError(
            "推送数据超时 (15秒)，请检查网络连接。数据已保存在本地，下次同步时将重试。"
        )
    except subprocess.CalledProcessError as e:
        output = e.stdout + e.stderr
        if "403" in output or "Permission denied" in output:
            raise SyncError(
                "推送权限不足。如果您是在新电脑上首次运行，请在终端手动执行一次 `git push` 以唤起 GitHub 登录授权弹窗。"
            )
        raise SyncError(f"推送数据失败: {output.strip()}")
