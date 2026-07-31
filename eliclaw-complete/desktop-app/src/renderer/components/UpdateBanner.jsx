import { Download } from 'lucide-react'

export default function UpdateBanner({ onClick }) {
  return (
    <div className="update-banner flex items-center justify-center gap-2" onClick={onClick}>
      <Download size={14} />
      <span>A new version of EliClaw is available. Click to install.</span>
    </div>
  )
}