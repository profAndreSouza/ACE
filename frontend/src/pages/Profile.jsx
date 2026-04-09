import { useState, useEffect } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { User, Mail, Phone, MapPin, CreditCard, Heart, Save, LogOut } from "lucide-react";
import { toast } from "sonner";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    phone: "",
    cpf: "",
    address: "",
    preferred_category: "",
    budget_range: "",
  });

  useEffect(() => {
    async function load() {
      const u = await autoelite.auth.me();
      setUser(u);
      setForm({
        phone: u.phone || "",
        cpf: u.cpf || "",
        address: u.address || "",
        preferred_category: u.preferred_category || "",
        budget_range: u.budget_range || "",
      });
      setLoading(false);
    }
    load();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    await autoelite.auth.updateMe(form);
    toast.success("Perfil atualizado com sucesso!");
    setSaving(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-muted border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="font-display text-3xl font-bold text-foreground">Meu Perfil</h1>
        <p className="text-muted-foreground mt-1">Gerencie suas informações pessoais e preferências.</p>
      </div>

      {/* Avatar & Basic Info */}
      <div className="bg-card rounded-xl border border-border p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-2xl font-bold">
            {user?.full_name?.charAt(0)?.toUpperCase() || "U"}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-foreground">{user?.full_name || "Usuário"}</h2>
            <p className="text-sm text-muted-foreground flex items-center gap-1">
              <Mail className="w-3.5 h-3.5" /> {user?.email}
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <FormField icon={Phone} label="Telefone" placeholder="(11) 99999-9999"
            value={form.phone} onChange={(v) => setForm(p => ({ ...p, phone: v }))} />
          <FormField icon={CreditCard} label="CPF" placeholder="000.000.000-00"
            value={form.cpf} onChange={(v) => setForm(p => ({ ...p, cpf: v }))} />
          <FormField icon={MapPin} label="Endereço" placeholder="Rua, número, cidade..."
            value={form.address} onChange={(v) => setForm(p => ({ ...p, address: v }))} />
        </div>
      </div>

      {/* Preferences */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
          <Heart className="w-5 h-5 text-primary" /> Preferências
        </h3>
        <p className="text-sm text-muted-foreground mb-4">Suas preferências nos ajudam a recomendar veículos ideais para você.</p>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1.5 block">Categoria Preferida</label>
            <Select value={form.preferred_category} onValueChange={(v) => setForm(p => ({ ...p, preferred_category: v }))}>
              <SelectTrigger><SelectValue placeholder="Selecione..." /></SelectTrigger>
              <SelectContent>
                {["SUV", "Sedan", "Hatch", "Picape", "Esportivo", "Elétrico"].map(c => (
                  <SelectItem key={c} value={c}>{c}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium mb-1.5 block">Faixa de Orçamento</label>
            <Select value={form.budget_range} onValueChange={(v) => setForm(p => ({ ...p, budget_range: v }))}>
              <SelectTrigger><SelectValue placeholder="Selecione..." /></SelectTrigger>
              <SelectContent>
                {["Até R$50.000", "R$50.000 - R$100.000", "R$100.000 - R$200.000", "Acima de R$200.000"].map(b => (
                  <SelectItem key={b} value={b}>{b}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <Button onClick={handleSave} disabled={saving} className="gap-2">
          <Save className="w-4 h-4" /> {saving ? "Salvando..." : "Salvar Perfil"}
        </Button>
        <Button variant="outline" onClick={() => autoelite.auth.logout()} className="gap-2 text-destructive">
          <LogOut className="w-4 h-4" /> Sair
        </Button>
      </div>
    </div>
  );
}

function FormField({ icon: Icon, label, placeholder, value, onChange }) {
  return (
    <div>
      <label className="text-sm font-medium mb-1.5 flex items-center gap-1.5 text-foreground">
        <Icon className="w-4 h-4 text-muted-foreground" /> {label}
      </label>
      <Input placeholder={placeholder} value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}