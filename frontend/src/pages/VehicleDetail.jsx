import { useState, useEffect } from "react";

import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Calendar, Fuel, Settings, Gauge, Palette, ShoppingCart } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription
} from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

const statusColors = {
  "Disponível": "bg-emerald-100 text-emerald-700",
  "Reservado": "bg-amber-100 text-amber-700",
  "Vendido": "bg-red-100 text-red-700",
};

export default function VehicleDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [vehicle, setVehicle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOrder, setShowOrder] = useState(false);
  const [orderData, setOrderData] = useState({ payment_method: "", notes: "" });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function load() {
      const vehicles = await autoelite.entities.Vehicle.filter({ id });
      if (vehicles.length > 0) setVehicle(vehicles[0]);
      setLoading(false);
    }
    load();
  }, [id]);

  const handleOrder = async () => {
    if (!orderData.payment_method) {
      toast.error("Selecione uma forma de pagamento");
      return;
    }
    setSubmitting(true);
    const user = await autoelite.auth.me();
    await autoelite.entities.Order.create({
      vehicle_id: vehicle.id,
      vehicle_name: `${vehicle.brand} ${vehicle.model}`,
      vehicle_image: vehicle.image_url || "",
      customer_name: user.full_name || "Cliente",
      customer_email: user.email,
      total_price: vehicle.price,
      payment_method: orderData.payment_method,
      status: "Pendente",
      notes: orderData.notes,
    });
    toast.success("Pedido realizado com sucesso!");
    setShowOrder(false);
    navigate("/pedidos");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-muted border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  if (!vehicle) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Veículo não encontrado.</p>
        <Button variant="outline" onClick={() => navigate("/veiculos")} className="mt-4">Voltar</Button>
      </div>
    );
  }

  const imageUrl = vehicle.image_url || "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=800&h=500&fit=crop";
  const specs = [
    { icon: Calendar, label: "Ano", value: vehicle.year },
    { icon: Fuel, label: "Combustível", value: vehicle.fuel_type },
    { icon: Settings, label: "Câmbio", value: vehicle.transmission },
    { icon: Gauge, label: "Motor", value: vehicle.engine },
    { icon: Palette, label: "Cor", value: vehicle.color },
  ].filter(s => s.value);

  return (
    <div className="space-y-6">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft className="w-4 h-4" /> Voltar
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Image */}
        <div className="rounded-2xl overflow-hidden border border-border">
          <img src={imageUrl} alt={`${vehicle.brand} ${vehicle.model}`} className="w-full h-72 lg:h-96 object-cover" />
        </div>

        {/* Info */}
        <div className="space-y-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge className={cn("text-xs", statusColors[vehicle.status] || statusColors["Disponível"])}>
                {vehicle.status || "Disponível"}
              </Badge>
              <Badge variant="outline">{vehicle.category}</Badge>
            </div>
            <p className="text-sm text-muted-foreground uppercase tracking-wider font-medium">{vehicle.brand}</p>
            <h1 className="font-display text-3xl font-bold text-foreground">{vehicle.model}</h1>
          </div>

          <div className="text-3xl font-bold text-primary">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(vehicle.price)}
          </div>

          {/* Specs Grid */}
          <div className="grid grid-cols-2 gap-3">
            {specs.map((spec, i) => (
              <div key={i} className="bg-muted/50 rounded-lg p-3 flex items-center gap-3">
                <spec.icon className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">{spec.label}</p>
                  <p className="text-sm font-medium text-foreground">{spec.value}</p>
                </div>
              </div>
            ))}
          </div>

          {vehicle.description && (
            <div>
              <h3 className="font-semibold text-sm text-foreground mb-2">Descrição</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{vehicle.description}</p>
            </div>
          )}

          {vehicle.features && (
            <div>
              <h3 className="font-semibold text-sm text-foreground mb-2">Características</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{vehicle.features}</p>
            </div>
          )}

          {(vehicle.status === "Disponível" || !vehicle.status) && (
            <Button onClick={() => setShowOrder(true)} size="lg" className="w-full gap-2">
              <ShoppingCart className="w-5 h-5" /> Fazer Pedido
            </Button>
          )}
        </div>
      </div>

      {/* Order Dialog */}
      <Dialog open={showOrder} onOpenChange={setShowOrder}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="font-display">Criar Pedido</DialogTitle>
            <DialogDescription>
              {vehicle.brand} {vehicle.model} — {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(vehicle.price)}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 mt-2">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Forma de Pagamento</label>
              <Select value={orderData.payment_method} onValueChange={(v) => setOrderData(prev => ({ ...prev, payment_method: v }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Financiamento">Financiamento</SelectItem>
                  <SelectItem value="À Vista">À Vista</SelectItem>
                  <SelectItem value="Consórcio">Consórcio</SelectItem>
                  <SelectItem value="Leasing">Leasing</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Observações</label>
              <Textarea
                placeholder="Alguma observação sobre o pedido?"
                value={orderData.notes}
                onChange={(e) => setOrderData(prev => ({ ...prev, notes: e.target.value }))}
              />
            </div>
            <Button onClick={handleOrder} disabled={submitting} className="w-full">
              {submitting ? "Processando..." : "Confirmar Pedido"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}