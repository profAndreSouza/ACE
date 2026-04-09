import { useState, useEffect } from "react";

import { Search, SlidersHorizontal, Car } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import VehicleCard from "../components/VehicleCard";

const categories = ["Todas", "SUV", "Sedan", "Hatch", "Picape", "Esportivo", "Elétrico"];

export default function Vehicles() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("Todas");
  const [sortBy, setSortBy] = useState("recent");

  useEffect(() => {
    async function load() {
      const data = await autoelite.entities.Vehicle.list("-created_date", 100);
      setVehicles(data);
      setLoading(false);
    }
    load();
  }, []);

  const filtered = vehicles
    .filter(v => {
      const matchSearch = !search || 
        `${v.brand} ${v.model}`.toLowerCase().includes(search.toLowerCase());
      const matchCategory = category === "Todas" || v.category === category;
      return matchSearch && matchCategory;
    })
    .sort((a, b) => {
      if (sortBy === "price_asc") return a.price - b.price;
      if (sortBy === "price_desc") return b.price - a.price;
      if (sortBy === "year") return b.year - a.year;
      return 0;
    });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-muted border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl font-bold text-foreground">Veículos</h1>
        <p className="text-muted-foreground mt-1">Explore nosso catálogo completo de veículos.</p>
      </div>

      {/* Filters */}
      <div className="bg-card rounded-xl border border-border p-4">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por marca ou modelo..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
          <Select value={category} onValueChange={setCategory}>
            <SelectTrigger className="w-full md:w-44">
              <SlidersHorizontal className="w-4 h-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {categories.map(c => (
                <SelectItem key={c} value={c}>{c}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-full md:w-44">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="recent">Mais Recentes</SelectItem>
              <SelectItem value="price_asc">Menor Preço</SelectItem>
              <SelectItem value="price_desc">Maior Preço</SelectItem>
              <SelectItem value="year">Mais Novo</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Results */}
      <p className="text-sm text-muted-foreground">{filtered.length} veículo(s) encontrado(s)</p>

      {filtered.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map(v => <VehicleCard key={v.id} vehicle={v} />)}
        </div>
      ) : (
        <div className="bg-card rounded-xl border border-border p-16 text-center">
          <Car className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="font-semibold text-foreground mb-1">Nenhum veículo encontrado</h3>
          <p className="text-sm text-muted-foreground">Tente ajustar seus filtros de busca.</p>
        </div>
      )}
    </div>
  );
}