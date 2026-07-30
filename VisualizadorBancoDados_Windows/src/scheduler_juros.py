"""
Módulo de agendamento para executar cálculos de juros todo dia 25 de cada mês
Usa APScheduler para agendar tarefas periódicas
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JurosScheduler:
    """Agendador para cálculos de juros automáticos"""
    
    def __init__(self, planilha_path: str, db_enabled: bool = True):
        """
        Inicializa o agendador
        
        Args:
            planilha_path: Caminho para a planilha_pu.xlsx
            db_enabled: Se o banco de dados está habilitado
        """
        self.planilha_path = planilha_path
        self.db_enabled = db_enabled
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        
        logger.info("[OK] JurosScheduler inicializado")
    
    def agendar_calculo_dia_25(self, hora: int = 10, minuto: int = 0):
        """
        Agenda o cálculo de juros para o dia 25 de cada mês
        
        Args:
            hora: Hora do dia (0-23, padrão: 10)
            minuto: Minuto da hora (0-59, padrão: 0)
        """
        try:
            # Criar trigger para executar no dia 25 de cada mês
            trigger = CronTrigger(
                day=25,
                hour=hora,
                minute=minuto,
                timezone='America/Sao_Paulo'  # Timezone do Brasil
            )
            
            self.scheduler.add_job(
                self._executar_calculo_juros,
                trigger=trigger,
                id='calculo_juros_dia_25',
                name='Cálculo de Juros - Dia 25',
                replace_existing=True
            )
            
            logger.info(f"[OK] Agendamento criado: Dia 25 às {hora:02d}:{minuto:02d}")
            
        except Exception as e:
            logger.error(f"[ERRO] Erro ao agendar cálculo: {e}")
    
    def _executar_calculo_juros(self):
        """Função interna que executa o cálculo de juros"""
        try:
            logger.info("=" * 80)
            logger.info(f"[INICIANDO] CÁLCULO DE JUROS - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            logger.info("=" * 80)
            
            from src.juros_calculator import JurosCalculator
            
            # Verificar se a planilha existe
            if not os.path.exists(self.planilha_path):
                logger.error(f"[ERRO] Planilha não encontrada: {self.planilha_path}")
                return
            
            # Criar calculadora
            calculadora = JurosCalculator(self.planilha_path)
            
            # Calcular para todos os ativos
            resultados = calculadora.calcular_juros_todos_ativos()
            calculadora.close()
            
            # Processar resultados
            total = len(resultados)
            sucessos = sum(1 for r in resultados.values() if r['sucesso'])
            erros = total - sucessos
            
            logger.info(f"[RESUMO] Resumo do cálculo:")
            logger.info(f"   Total de ativos: {total}")
            logger.info(f"   Sucessos: {sucessos}")
            logger.info(f"   Erros: {erros}")
            
            # Salvar no banco de dados se habilitado
            if self.db_enabled:
                try:
                    from src.database import salvar_calculo_juros
                    
                    for codigo_if, resultado in resultados.items():
                        if resultado['sucesso']:
                            salvar_calculo_juros(
                                codigo_if,
                                resultado['data'],
                                resultado['vna'],
                                resultado['porcentagem'],
                                resultado['juros_calculado']
                            )
                            logger.info(f"   [OK] {codigo_if}: {resultado['juros_calculado']}")
                        else:
                            logger.warning(f"   [ERRO] {codigo_if}: {resultado['erro']}")
                
                except Exception as db_error:
                    logger.error(f"[AVISO] Erro ao salvar no banco de dados: {db_error}")
            
            logger.info("=" * 80)
            logger.info(f"[OK] CÁLCULO CONCLUÍDO - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"[ERRO] Erro ao executar cálculo de juros: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def agendar_teste(self, segundos: int = 60):
        """
        Agenda um teste de execução para validar a configuração
        
        Args:
            segundos: Segundos até a próxima execução
        """
        try:
            from apscheduler.triggers.date import DateTrigger
            from datetime import datetime, timedelta
            
            proxima_execucao = datetime.now() + timedelta(seconds=segundos)
            
            trigger = DateTrigger(run_date=proxima_execucao)
            
            self.scheduler.add_job(
                self._executar_calculo_juros,
                trigger=trigger,
                id='teste_calculo_juros',
                name='Teste de Cálculo de Juros'
            )
            
            logger.info(f"[OK] Teste agendado para {proxima_execucao.strftime('%d/%m/%Y %H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"[ERRO] Erro ao agendar teste: {e}")
    
    def listar_jobs(self):
        """Lista todos os jobs agendados"""
        jobs = self.scheduler.get_jobs()
        logger.info(f"[JOBS] Jobs agendados: {len(jobs)}")
        
        for job in jobs:
            logger.info(f"   - {job.name} (ID: {job.id})")
            logger.info(f"     Próxima execução: {job.next_run_time}")
        
        return jobs
    
    def remover_job(self, job_id: str):
        """Remove um job agendado"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"[OK] Job removido: {job_id}")
        except Exception as e:
            logger.error(f"[ERRO] Erro ao remover job: {e}")
    
    def pausar_scheduler(self):
        """Pausa o agendador"""
        try:
            self.scheduler.pause()
            logger.info("[PAUSADO] Agendador pausado")
        except Exception as e:
            logger.error(f"[ERRO] Erro ao pausar agendador: {e}")
    
    def retomar_scheduler(self):
        """Retoma o agendador"""
        try:
            self.scheduler.resume()
            logger.info("[ATIVO] Agendador retomado")
        except Exception as e:
            logger.error(f"[ERRO] Erro ao retomar agendador: {e}")
    
    def parar_scheduler(self):
        """Para o agendador"""
        try:
            self.scheduler.shutdown()
            logger.info("[PARADO] Agendador parado")
        except Exception as e:
            logger.error(f"[ERRO] Erro ao parar agendador: {e}")


# Instância global do scheduler
_scheduler_instance = None


def inicializar_scheduler(planilha_path: str, db_enabled: bool = True) -> JurosScheduler:
    """
    Factory function para inicializar o scheduler global
    
    Args:
        planilha_path: Caminho para a planilha_pu.xlsx
        db_enabled: Se o banco de dados está habilitado
        
    Returns:
        Instância de JurosScheduler
    """
    global _scheduler_instance
    
    if _scheduler_instance is None:
        _scheduler_instance = JurosScheduler(planilha_path, db_enabled)
    
    return _scheduler_instance


def obter_scheduler() -> JurosScheduler:
    """Obtém a instância global do scheduler"""
    global _scheduler_instance
    
    if _scheduler_instance is None:
        raise RuntimeError("Scheduler não foi inicializado. Chame inicializar_scheduler() primeiro.")
    
    return _scheduler_instance
