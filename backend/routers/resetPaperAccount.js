import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end('Method Not Allowed');

  try {
    // Example: delete or reset your paper account files
    // Adjust paths to your real data folders
    const paperDataDir = path.resolve(process.cwd(), 'data_paper');

    // Here you could delete files, or overwrite with initial empty state
    // WARNING: Be careful and maybe backup important files!

    // Example: clear portfolio snapshot file
    const portfolioFile = path.join(paperDataDir, 'portfolio_snapshot.json');
    if (fs.existsSync(portfolioFile)) {
      fs.writeFileSync(portfolioFile, JSON.stringify({ totalPortfolio: 0, availableUSD: 0, coins: {} }));
    }

    // TODO: clear other files similarly...

    return res.status(200).json({ message: 'Paper account reset successfully' });
  } catch (error) {
    console.error('Reset paper account error:', error);
    return res.status(500).json({ message: 'Failed to reset paper account' });
  }
}