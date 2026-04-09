import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import moment from "moment";

const statusConfig = {
  "Pendente": { color: "bg-yellow-100 text-yellow-700", dot: "bg-yellow-500" },
  "Confirmado": { color: "bg-blue-100 text-blue-700", dot: "bg-blue-500" },
  "Em Produção": { color: "bg-purple-100 text-purple-700", dot: "bg-purple-500" },
  "Pronto para Entrega": { color: "bg-emerald-100 text-emerald-700", dot: "bg-emerald-500" },
  "Entregue": { color: "bg-green-100 text-green-700", dot: "bg-green-500" },
  "Cancelado": { color: "bg-red-100 text-red-700", dot: "bg-red-500" },
};

export default function OrderCard({ order }) {
  const config = statusConfig[order.status] || statusConfig["Pendente"];
  const imageUrl = order.vehicle_image || "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=200&h=150&fit=crop";

  return (
    <Link to={`/pedidos/${order.id}`} className="group block">
      <div className="bg-card rounded-xl border border-border p-4 hover:shadow-lg transition-all duration-300 hover:border-primary/20">
        <div className="flex items-center gap-4">
          <img
            src={imageUrl}
            alt={order.vehicle_name}
            className="w-20 h-16 rounded-lg object-cover flex-shrink-0"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-foreground truncate">{order.vehicle_name}</h3>
              <Badge className={cn("text-xs flex-shrink-0", config.color)}>
                <span className={cn("w-1.5 h-1.5 rounded-full mr-1.5", config.dot)} />
                {order.status}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              {order.payment_method} · {moment(order.created_date).format("DD/MM/YYYY")}
            </p>
            <p className="text-sm font-bold text-primary mt-1">
              {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(order.total_price)}
            </p>
          </div>
          <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors flex-shrink-0" />
        </div>
      </div>
    </Link>
  );
}