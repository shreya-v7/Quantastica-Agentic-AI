module.exports = {
    darkMode: ["class"],
    content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
  	extend: {
  		fontFamily: {
  			sans: [
  				'"Plus Jakarta Sans"',
  				"ui-sans-serif",
  				"system-ui",
  				"-apple-system",
  				"Segoe UI",
  				"Roboto",
  				"sans-serif",
  			],
  		},
  		fontSize: {
  			"2xs": ["0.6875rem", { lineHeight: "1rem", letterSpacing: "0.06em" }],
  		},
  		boxShadow: {
  			fi: "0 1px 0 0 hsl(var(--border) / 0.6), 0 18px 40px -24px hsl(222 47% 11% / 0.12)",
  			"fi-dark": "0 1px 0 0 hsl(var(--border) / 0.5), 0 24px 48px -20px hsl(0 0% 0% / 0.45)",
  		},
  		colors: {
  			background: 'hsl(var(--background))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			foreground: 'hsl(var(--foreground))',
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			},
  			surface: {
  				DEFAULT: "hsl(var(--surface))",
  				elevated: "hsl(var(--surface-elevated))",
  			},
  			/* Legacy aliases — align with primary / violet for uniform UI */
  			accentBlue: {
  				DEFAULT: "hsl(var(--primary))",
  			},
  			accentPurple: {
  				DEFAULT: "hsl(262 52% 58%)",
  			},
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		}
  	}
  },
    plugins: [require("tailwindcss-animate")]
}