import { useState, useEffect } from "react";

import { Sparkles, RefreshCw, UserCog } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import VehicleCard from "../components/VehicleCard";

export default function Recommendations() {
  const [vehicles, setVehicles] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadRecommendations = async () => {
    setLoading(true);
    const [allVehicles, currentUser] = await Promise.all([
      autoelite.entities.Vehicle.list("-created_date", 100),
      autoelite.auth.me(),
    ]);
    setVehicles(allVehicles);
    setUser(currentUser);

    const available = allVehicles.filter(v => v.status === "Disponível" || !v.status);

    // Filter by user preferences
    let matched = [];
    if (currentUser.preferred_category) {
      matched = available.filter(v => v.category === currentUser.preferred_category);
    }

    // Budget filtering
    if (currentUser.budget_range) {
      const budgetFilter = getBudgetRange(currentUser.budget_range);
      const budgetMatched = available.filter(v => v.price >= budgetFilter.min && v.price <= budgetFilter.max);
      if (matched.length > 0) {
        matched = matched.filter(v => budgetMatched.some(bv => bv.id === v.id));
      } else {
        matched = budgetMatched;
      }
    }

    // If no preferences or no matches, show latest
    if (matched.length === 0) {
      matched = available.slice(0, 6);
    }

    setRecommendations(matched.slice(0, 6));
    setLoading(false);
  };

  useEffect(() => {
    loadRecommendations();
  }, []);

  const hasPreferences = user?.preferred_category || user?.budget_range;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-muted border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold text-foreground flex items-center gap-2">
            <Sparkles className="w-8 h-8 text-secondary" /> Para Você
          </h1>
          <p className="text-muted-foreground mt-1">Recomendações personalizadas baseadas no seu perfil.</p>
        </div>
        <Button variant="outline" onClick={loadRecommendations} className="gap-2">
          <RefreshCw className="w-4 h-4" /> Atualizar
        </Button>
      </div>

      {!hasPreferences && (
        <div className="bg-secondary/10 border border-secondary/20 rounded-xl p-5 flex flex-col md:flex-row items-start md:items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center flex-shrink-0">
            <UserCog className="w-6 h-6 text-secondary" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-foreground">Complete seu perfil</h3>
            <p className="text-sm text-muted-foreground">
              Adicione suas preferências de categoria e faixa de orçamento para receber recomendações mais assertivas.
            </p>
          </div>
          <Link to="/perfil">
            <Button variant="secondary" size="sm">Ir para o Perfil</Button>
          </Link>
        </div>
      )}

      {hasPreferences && (
        <div className="flex flex-wrap gap-2">
          {user.preferred_category && (
            <div className="bg-primary/10 text-primary text-sm font-medium px-3 py-1.5 rounded-full">
              Categoria: {user.preferred_category}
            </div>
          )}
          {user.budget_range && (
            <div className="bg-secondary/10 text-secondary-foreground text-sm font-medium px-3 py-1.5 rounded-full">
              Orçamento: {user.budget_range}
            </div>
          )}
        </div>
      )}

      {recommendations.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {recommendations.map(v => <VehicleCard key={v.id} vehicle={v} />)}
        </div>
      ) : (
        <div className="bg-card rounded-xl border border-border p-16 text-center">
          <Sparkles className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="font-semibold text-foreground mb-1">Nenhuma recomendação disponível</h3>
          <p className="text-sm text-muted-foreground">Adicione veículos ao catálogo para ver recomendações.</p>
        </div>
      )}
    </div>
  );
}

function getBudgetRange(range) {
  switch (range) {
    case "Até R$50.000": return { min: 0, max: 50000 };
    case "R$50.000 - R$100.000": return { min: 50000, max: 100000 };
    case "R$100.000 - R$200.000": return { min: 100000, max: 200000 };
    case "Acima de R$200.000": return { min: 200000, max: Infinity };
    default: return { min: 0, max: Infinity };
  }
}