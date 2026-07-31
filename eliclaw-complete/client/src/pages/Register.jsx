import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import { Eye, EyeOff, ArrowRight, Zap, Check } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const { register, isLoading } = useAuthStore()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!name || !email || !password) {
      toast.error('Please fill in all fields')
      return
    }
    if (password.length < 6) {
      toast.error('Password must be at least 6 characters')
      return
    }
    const result = await register(name, email, password)
    if (result.success) {
      toast.success('Account created! Welcome to EliClaw.')
      window.location.href = '/dashboard'
    } else {
      toast.error(result.error || 'Registration failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-900 px-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-cyan-400 rounded-xl flex items-center justify-center">
              <Zap size={24} className="text-white" />
            </div>
            <span className="text-2xl font-bold gradient-text">EliClaw</span>
          </Link>
          <h1 className="text-3xl font-bold mb-2">Create your account</h1>
          <p className="text-dark-400">Start with 3 free audits per month</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              className="input-field"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              className="input-field"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="input-field pr-12"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-dark-500 hover:text-white"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isLoading ? 'Creating account...' : <>Create Account <ArrowRight size={18} /></>}
          </button>
        </form>

        <div className="mt-6 p-4 bg-dark-800/50 rounded-xl border border-dark-700/50">
          <div className="flex items-start gap-3">
            <Check size={18} className="text-green-400 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-dark-400">
              <p className="text-white font-medium mb-1">Free plan includes:</p>
              <ul className="space-y-1">
                <li>3 SEO audits per month</li>
                <li>1 competitor analysis</li>
                <li>Basic website analyzer</li>
                <li>Community support</li>
              </ul>
            </div>
          </div>
        </div>

        <p className="text-center mt-6 text-dark-400">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}