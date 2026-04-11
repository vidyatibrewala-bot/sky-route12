import fs from 'fs';
import path from 'path';

const TOKEN = process.env.HF_TOKEN; // Use environment variable
const REPO_ID = "happyjourney1/skyroute-dashboard";
const API = "https://huggingface.co/api/spaces";

// Collect all files to upload
const FILES = [
    "Dockerfile",
    "requirements.txt",
    "inference.py",
    "drone_env.py",
    "openenv.yaml",
    "README.md",
    "pyproject.toml",
    "ppo_drone_aid.zip",
    "netlify.toml",
    "server/__init__.py",
    "server/app.py",
    "server/drone_dashboard.py",
    "server/drone_env.py",
    "server/graders.py",
];

function walkDir(dir) {
    const results = [];
    if (!fs.existsSync(dir)) return results;
    for (const f of fs.readdirSync(dir)) {
        const full = path.join(dir, f);
        if (fs.statSync(full).isDirectory()) {
            results.push(...walkDir(full));
        } else {
            results.push(full.replace(/\\/g, '/'));
        }
    }
    return results;
}

const frontendFiles = walkDir('frontend');
const allFiles = [...FILES, ...frontendFiles].filter(f => fs.existsSync(f));

console.log(`[INFO] ${allFiles.length} files to upload to ${REPO_ID}`);

// Step 1: Ensure Space exists
async function ensureRepo() {
    const res = await fetch("https://huggingface.co/api/repos/create", {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${TOKEN}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: "skyroute-dashboard",
            type: "space",
            sdk: "docker",
            private: false
        })
    });
    const text = await res.text();
    console.log(`[REPO] Status: ${res.status} - ${text.substring(0, 100)}`);
}

// Step 2: Upload each file individually using the upload endpoint
async function uploadFile(filePath) {
    const remotePath = filePath.replace(/\\/g, '/');
    const content = fs.readFileSync(filePath);

    const url = `${API}/${REPO_ID}/upload/main/${remotePath}`;

    const res = await fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${TOKEN}`,
            'Content-Type': 'application/octet-stream',
        },
        body: content
    });

    if (res.ok) {
        console.log(`[OK] ${remotePath}`);
    } else {
        const text = await res.text();
        console.log(`[FAIL] ${remotePath}: ${res.status} - ${text.substring(0, 150)}`);
    }
}

async function main() {
    await ensureRepo();

    for (const file of allFiles) {
        await uploadFile(file);
    }

    console.log(`\n[DONE] https://huggingface.co/spaces/${REPO_ID}`);
}

main().catch(err => { console.error('[FATAL]', err); process.exit(1); });
