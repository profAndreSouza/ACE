import { Button } from "@/components/ui/button";
import { Car, ShieldCheck, Truck, Sparkles, Star, ChevronRight, Zap } from "lucide-react";
import { Link } from "react-router-dom";

const FEATURES = [
  { icon: Car, title: "Catálogo Completo", desc: "Explore centenas de veículos com filtros avançados de categoria, preço e especificações." },
  { icon: ShieldCheck, title: "Compra Segura", desc: "Processo de pedido transparente com acompanhamento em tempo real de cada etapa." },
  { icon: Truck, title: "Acompanhe sua Entrega", desc: "Timeline detalhada do seu pedido, da confirmação até a entrega final." },
  { icon: Sparkles, title: "Recomendações Inteligentes", desc: "Sugestões personalizadas baseadas no seu perfil, preferências e orçamento." },
];

const BRANDS = ["Toyota", "BMW", "Mercedes", "Porsche", "Ford", "BYD", "Volkswagen", "Audi"];

const TESTIMONIALS = [
  { name: "Carlos M.", text: "Comprei meu BMW pelo portal e a experiência foi incrível. Acompanhei tudo pela timeline!", stars: 5 },
  { name: "Ana P.", text: "As recomendações me ajudaram a encontrar o carro perfeito dentro do meu orçamento.", stars: 5 },
  { name: "Roberto S.", text: "Atendimento impecável e processo de pedido muito transparente. Recomendo!", stars: 5 },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navbar */}
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center">
              <Car className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-display text-xl font-bold text-foreground">AutoElite</span>
          </div>
          <Button className="gap-2">
            Entrar <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden bg-primary text-primary-foreground py-24 px-4">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1400&h=700&fit=crop')] bg-cover bg-center opacity-10" />
        <div className="relative max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-1.5 mb-6 text-sm font-medium">
            <Zap className="w-4 h-4" /> Nova experiência de compra digital
          </div>
          <h1 className="font-display text-5xl md:text-6xl font-bold leading-tight mb-6">
            Encontre o carro<br />
            <span className="text-white/70">dos seus sonhos</span>
          </h1>
          <p className="text-lg text-primary-foreground/80 max-w-2xl mx-auto mb-10">
            A concessionária digital que combina tecnologia, transparência e atendimento premium.
            Compre, acompanhe e receba — tudo online.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Button
              size="lg"
              variant="secondary"
              // onClick={() => }
              className="gap-2 bg-white text-primary hover:bg-white/90 px-8"
            >
              Começar agora <ChevronRight className="w-5 h-5" />
            </Button>
            <a href="#features" className="text-primary-foreground/80 hover:text-white text-sm font-medium flex items-center gap-1">
              Saiba mais ↓
            </a>
          </div>
        </div>
      </section>

      {/* Stats Banner */}
      <section className="bg-card border-b border-border py-8 px-4">
        <div className="max-w-5xl mx-auto grid grid-cols-3 gap-8 text-center">
          <div>
            <p className="text-3xl font-bold text-primary">500+</p>
            <p className="text-sm text-muted-foreground mt-1">Veículos no Catálogo</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-primary">98%</p>
            <p className="text-sm text-muted-foreground mt-1">Clientes Satisfeitos</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-primary">15+</p>
            <p className="text-sm text-muted-foreground mt-1">Marcas Disponíveis</p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="font-display text-4xl font-bold text-foreground mb-3">Por que escolher a AutoElite?</h2>
            <p className="text-muted-foreground text-lg max-w-xl mx-auto">Uma plataforma completa para a melhor experiência de compra automotiva.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map((f, i) => (
              <div key={i} className="bg-card rounded-xl border border-border p-6 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                  <f.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Brands */}
      <section className="py-12 px-4 bg-muted/30">
        <div className="max-w-5xl mx-auto text-center">
          <p className="text-sm text-muted-foreground uppercase tracking-widest mb-8">Marcas disponíveis</p>
          <div className="flex flex-wrap justify-center gap-4">
            {BRANDS.map(b => (
              <div key={b} className="bg-card border border-border rounded-lg px-5 py-2.5 text-sm font-semibold text-foreground hover:border-primary/40 transition-colors">
                {b}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="font-display text-4xl font-bold text-foreground text-center mb-12">O que nossos clientes dizem</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t, i) => (
              <div key={i} className="bg-card border border-border rounded-xl p-6">
                <div className="flex gap-0.5 mb-3">
                  {Array.from({ length: t.stars }).map((_, j) => (
                    <Star key={j} className="w-4 h-4 fill-primary text-primary" />
                  ))}
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed mb-4">"{t.text}"</p>
                <p className="text-sm font-semibold text-foreground">{t.name}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 bg-primary text-primary-foreground">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="font-display text-4xl font-bold mb-4">Pronto para encontrar seu próximo veículo?</h2>
          <p className="text-primary-foreground/80 mb-8 text-lg">Crie sua conta gratuitamente e acesse o catálogo completo.</p>
          <Button
            size="lg"
            // onClick={() => autoelite.auth.redirectToLogin("/dashboard")}
            className="bg-white text-primary hover:bg-white/90 px-10 gap-2"
          >
            Criar conta grátis <ChevronRight className="w-5 h-5" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-8 px-4 text-center text-sm text-muted-foreground">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Car className="w-4 h-4 text-primary" />
          <span className="font-semibold text-foreground">AutoElite</span>
        </div>
        <p>© 2026 AutoElite Concessionária. Todos os direitos reservados.</p>
      </footer>
    </div>
  );
}