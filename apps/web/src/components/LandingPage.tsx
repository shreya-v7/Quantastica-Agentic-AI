import { useState, useEffect } from 'react';
import { Wallet, LineChart, ShieldCheck, Users, ArrowRight, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';

const features = [
  {
    title: "Talk to Your Wallet",
    icon: <Wallet className="w-8 h-8" />,
    color: "from-cyan-400 to-blue-500",
    description: "Natural voice conversations with your AI financial assistant",
  },
  {
    title: "Get Real-Time Tips",
    icon: <LineChart className="w-8 h-8" />,
    color: "from-blue-400 to-indigo-500",
    description: "Smart insights and predictions powered by advanced AI",
  },
  {
    title: "Encrypted Voice Logs",
    icon: <ShieldCheck className="w-8 h-8" />,
    color: "from-green-400 to-emerald-500",
    description: "Bank-level security for all your financial conversations",
  },
  {
    title: "Team Calls & Co-Invest",
    icon: <Users className="w-8 h-8" />,
    color: "from-purple-400 to-pink-500",
    description: "Collaborate with friends and family on investment decisions",
  },
];

const LandingPage = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => setMousePosition({ x: e.clientX, y: e.clientY });
    const handleScroll = () => setScrollY(window.scrollY);

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      {/* Background with subtle gradient and radial effect */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-black via-blue-950 to-black"></div>
        <div
          className="absolute inset-0 opacity-20 pointer-events-none"
          style={{
            background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(56, 189, 248, 0.15) 0%, transparent 70%)`,
          }}
        ></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 px-6 lg:px-12 py-6 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-lg blur-lg opacity-70 animate-pulse"></div>
            <div className="relative bg-gradient-to-r from-cyan-400 to-blue-500 p-2 rounded-lg">
              <Wallet className="w-6 h-6 text-white" />
            </div>
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            FinanceAI
          </span>
        </div>

        <div className="hidden md:flex items-center space-x-8">
          <a href="#features" className="hover:text-cyan-400 transition-colors">
            Features
          </a>
          <a href="#how" className="hover:text-cyan-400 transition-colors">
            How it Works
          </a>
          <a href="#pricing" className="hover:text-cyan-400 transition-colors">
            Pricing
          </a>
          <a
            href="/auth"
            className="px-6 py-2 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full hover:shadow-lg hover:shadow-cyan-400/40 transition-all transform hover:scale-105"
          >
            Sign In
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 px-6 lg:px-12 py-20 lg:py-32 max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
        <motion.div
          initial={{ opacity: 0, x: -40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7 }}
          className="space-y-8"
        >
          <h1 className="text-5xl lg:text-7xl font-bold leading-tight">
            <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Your Money,
            </span>
            <br />
            <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Now Speaks
            </span>
          </h1>
          <p className="text-xl text-gray-400 leading-relaxed">
            Have natural conversations with your AI financial assistant. Track expenses, get investment tips,
            and make smarter money decisions—all through voice.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <a
              href="/auth"
              className="group px-8 py-4 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full font-semibold hover:shadow-lg hover:shadow-cyan-400/25 transition-all transform hover:scale-105 flex items-center justify-center"
            >
              Start Free Trial
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </a>
            <button className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-white/10 rounded-full font-semibold hover:bg-white/10 transition-all">
              Watch Demo
            </button>
          </div>
        </motion.div>

        {/* AI Assistant chat box */}
        <motion.div
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="relative bg-gradient-to-br from-blue-900/20 to-cyan-900/20 backdrop-blur-xl rounded-3xl p-8 border border-white/10 shadow-lg"
          style={{ boxShadow: '0 0 25px rgba(14, 116, 144, 0.6)' }}
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2 text-cyan-400 font-semibold text-lg">
              <Wallet className="w-8 h-8" />
              <span>AI Assistant</span>
            </div>
            <div className="flex space-x-1">
              <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
              <div className="w-3 h-3 rounded-full bg-red-400"></div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-white/5 rounded-2xl p-4 backdrop-blur-sm">
              <p className="text-sm text-gray-300 mb-2">You said:</p>
              <p className="text-white">"How much did I spend on dining this month?"</p>
            </div>

            <div className="bg-gradient-to-r from-cyan-400/10 to-blue-500/10 rounded-2xl p-4 backdrop-blur-sm border border-cyan-400/20">
              <p className="text-sm text-cyan-400 mb-2">AI Assistant:</p>
              <p className="text-white">
                You've spent $487 on dining this month, which is 23% more than last month. I notice you eat out most
                on weekends. Would you like some tips to save?
              </p>
            </div>

            <div className="flex items-center justify-center py-4">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 px-6 lg:px-12 py-20 max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Powerful Features</span>
          </h2>
          <p className="text-xl text-gray-400">Everything you need to master your finances</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * index, duration: 0.6 }}
              className="group relative"
              style={{
                transform: `translateY(${scrollY * 0.05 * (index + 1)}px)`,
              }}
            >
              <div
                className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl blur-xl"
                style={{
                  background: `linear-gradient(to right, var(--tw-gradient-stops))`,
                  ['--tw-gradient-from' as any]: feature.color.split(' ')[0],
                  ['--tw-gradient-to' as any]: feature.color.split(' ')[2],
                } as React.CSSProperties}
              ></div>
              <div className="relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all h-full shadow-md hover:shadow-cyan-500/30">
                <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${feature.color} mb-4`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how" className="relative z-10 px-6 lg:px-12 py-20 max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">How It Works</span>
          </h2>
          <p className="text-xl text-gray-400">Get started in 3 simple steps</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            { step: '01', title: 'Connect Your Accounts', desc: 'Securely link your bank accounts and cards' },
            { step: '02', title: 'Start Talking', desc: 'Ask questions and get instant insights' },
            { step: '03', title: 'Make Better Decisions', desc: 'Act on personalized recommendations' },
          ].map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * i, duration: 0.6 }}
              className="relative group"
            >
              <div className="absolute top-0 left-0 text-8xl font-bold text-white/5 group-hover:text-cyan-400/10 transition-colors">
                {item.step}
              </div>
              <div className="relative pt-8">
                <h3 className="text-2xl font-semibold mb-3">{item.title}</h3>
                <p className="text-gray-400">{item.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 px-6 lg:px-12 py-20 max-w-4xl mx-auto text-center">
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-3xl blur-3xl opacity-20"></div>
          <div className="relative bg-gradient-to-r from-cyan-400/10 to-blue-500/10 backdrop-blur-xl rounded-3xl p-12 border border-white/10 shadow-lg">
            <h2 className="text-4xl lg:text-5xl font-bold mb-6">Ready to Transform Your Finances?</h2>
            <p className="text-xl text-gray-300 mb-8">
              Join thousands who are already making smarter money decisions with AI
            </p>
            <a
              href="/auth"
              className="group px-8 py-4 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full font-semibold hover:shadow-lg hover:shadow-cyan-400/25 transition-all transform hover:scale-105 inline-flex items-center justify-center"
            >
              Get Started Free
              <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
