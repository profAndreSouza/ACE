import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Fuel, Settings, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";

const statusColors = {
  "Disponível": "bg-emerald-100 text-emerald-700",
  "Reservado": "bg-amber-100 text-amber-700",
  "Vendido": "bg-red-100 text-red-700",
};

export default function VehicleCard({ vehicle }) {
  const imageUrl = vehicle.image_url || `https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=600&h=400&fit=crop`;

  return (
    <Link to={`/veiculos/${vehicle.id}`} className="group block">
      <div className="bg-card rounded-xl overflow-hidden border border-border shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
        <div className="relative h-48 overflow-hidden">
          <img
            src={imageUrl}
            alt={`${vehicle.brand} ${vehicle.model}`}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute top-3 left-3">
            <Badge className={cn("text-xs font-medium", statusColors[vehicle.status] || statusColors["Disponível"])}>
              {vehicle.status || "Disponível"}
            </Badge>
          </div>
          <div className="absolute top-3 right-3">
            <Badge variant="secondary" className="bg-black/60 text-white border-0 text-xs">
              {vehicle.category}
            </Badge>
          </div>
        </div>
        <div className="p-4">
          <div className="flex items-start justify-between mb-2">
            <div>
              <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{vehicle.brand}</p>
              <h3 className="font-display text-lg font-semibold text-foreground">{vehicle.model}</h3>
            </div>
          </div>
          <div className="flex items-center gap-3 text-xs text-muted-foreground mb-3">
            <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" />{vehicle.year}</span>
            {vehicle.fuel_type && <span className="flex items-center gap-1"><Fuel className="w-3.5 h-3.5" />{vehicle.fuel_type}</span>}
            {vehicle.transmission && <span className="flex items-center gap-1"><Settings className="w-3.5 h-3.5" />{vehicle.transmission}</span>}
          </div>
          <div className="pt-3 border-t border-border">
            <p className="text-xl font-bold text-primary">
              {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(vehicle.price)}
            </p>
          </div>
        </div>
      </div>
    </Link>
  );
}