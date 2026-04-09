import { useState, useEffect } from "react";

import { useParams, useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Car, CreditCard, FileText, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";
import moment from "moment";
import ProductionTimeline from "../components/ProductionTimeline";

const statusConfig = {
  "Pendente": "bg-yellow-100 text-yellow-700",
  "Confirmado": "bg-blue-100 text-blue-700",
  "Em Produção": "bg-purple-100 text-purple-700",
  "Pronto para Entrega": "bg-emerald-100 text-emerald-700",
  "Entregue": "bg-green-100 text-green-700",
  "Cancelado": "bg-red-100 text-red-700",
};

export default function OrderDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const orders = await autoelite.entities.Order.filter({ id });
      if (orders.length > 0) setOrder(orders[0]);
      setLoading(false);
    }
    load();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-muted border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  if (!order) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Pedido não encontrado.</p>
        <Button variant="outline" onClick={() => navigate("/pedidos")} className="mt-4">Voltar</Button>
      </div>
    );
  }

  const imageUrl = order.vehicle_image || "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=400&h=300&fit=crop";

  return (
    <div className="space-y-6">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft className="w-4 h-4" /> Voltar
      </button>

      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold text-foreground">Pedido #{order.id?.slice(-6)}</h1>
          <p className="text-sm text-muted-foreground">Criado em {moment(order.created_date).format("DD/MM/YYYY [às] HH:mm")}</p>
        </div>
        <Badge className={cn("text-sm px-4 py-1.5", statusConfig[order.status])}>
          {order.status}
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Vehicle */}
          <div className="bg-card rounded-xl border border-border p-5">
            <h2 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <Car className="w-5 h-5 text-primary" /> Veículo
            </h2>
            <div className="flex items-center gap-4">
              <img src={imageUrl} alt={order.vehicle_name} className="w-24 h-20 rounded-lg object-cover" />
              <div>
                <h3 className="font-semibold text-foreground">{order.vehicle_name}</h3>
                <Link to={`/veiculos/${order.vehicle_id}`} className="text-sm text-primary hover:underline">
                  Ver detalhes do veículo →
                </Link>
              </div>
            </div>
          </div>

          {/* Details */}
          <div className="bg-card rounded-xl border border-border p-5">
            <h2 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" /> Detalhes do Pedido
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <InfoItem icon={CreditCard} label="Pagamento" value={order.payment_method} />
              <InfoItem icon={Calendar} label="Data" value={moment(order.created_date).format("DD/MM/YYYY")} />
            </div>
            <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Valor Total</span>
              <span className="text-2xl font-bold text-primary">
                {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(order.total_price)}
              </span>
            </div>
            {order.notes && (
              <div className="mt-4 pt-4 border-t border-border">
                <p className="text-sm text-muted-foreground mb-1">Observações</p>
                <p className="text-sm text-foreground">{order.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* Timeline */}
        <div className="bg-card rounded-xl border border-border p-5">
          <h2 className="font-semibold text-foreground mb-6">Acompanhamento</h2>
          <ProductionTimeline status={order.status} />
        </div>
      </div>
    </div>
  );
}

function InfoItem({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
        <Icon className="w-4 h-4 text-muted-foreground" />
      </div>
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm font-medium text-foreground">{value || "—"}</p>
      </div>
    </div>
  );
}