import { CheckCircle, Circle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

const defaultSteps = [
  { name: "Pedido Recebido", description: "Seu pedido foi registrado" },
  { name: "Confirmação", description: "Pagamento e documentação verificados" },
  { name: "Preparação", description: "Veículo em preparação e inspeção" },
  { name: "Revisão Final", description: "Verificações finais de qualidade" },
  { name: "Pronto para Entrega", description: "Veículo pronto, agende a retirada" },
  { name: "Entregue", description: "Veículo entregue ao cliente" },
];

const statusToStep = {
  "Pendente": 0,
  "Confirmado": 1,
  "Em Produção": 2,
  "Pronto para Entrega": 4,
  "Entregue": 5,
  "Cancelado": -1,
};

export default function ProductionTimeline({ status }) {
  const currentStep = statusToStep[status] ?? 0;

  if (status === "Cancelado") {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <p className="text-red-700 font-medium">Pedido cancelado</p>
      </div>
    );
  }

  return (
    <div className="space-y-0">
      {defaultSteps.map((step, index) => {
        const isCompleted = index <= currentStep;
        const isCurrent = index === currentStep;
        const isLast = index === defaultSteps.length - 1;

        return (
          <div key={index} className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300",
                isCompleted
                  ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                  : isCurrent
                    ? "bg-secondary text-secondary-foreground shadow-lg shadow-secondary/20"
                    : "bg-muted text-muted-foreground"
              )}>
                {isCompleted ? (
                  <CheckCircle className="w-5 h-5" />
                ) : isCurrent ? (
                  <Clock className="w-5 h-5" />
                ) : (
                  <Circle className="w-5 h-5" />
                )}
              </div>
              {!isLast && (
                <div className={cn(
                  "w-0.5 h-12 transition-colors",
                  isCompleted ? "bg-primary" : "bg-muted"
                )} />
              )}
            </div>
            <div className="pb-8">
              <h4 className={cn(
                "font-semibold text-sm",
                isCompleted ? "text-foreground" : "text-muted-foreground"
              )}>
                {step.name}
              </h4>
              <p className="text-xs text-muted-foreground mt-0.5">{step.description}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}