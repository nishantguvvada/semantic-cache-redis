from fastapi import FastAPI
from pydantic import BaseModel
from graph import compiled_graph
import logging
import uvicorn
import time
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

metrics.set_meter_provider(
    MeterProvider(
        metric_readers=[
            PeriodicExportingMetricReader(ConsoleMetricExporter())
        ]
    )
)

LoggingInstrumentor().instrument(set_logging_format=True)

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get('/')
def default():
    start = time.perf_counter()
    time.sleep(3)
    logger.info(f"Processing time: {start - time.perf_counter()}")
    return { "response": "working" }

class InputQuery(BaseModel):
    query: str

@app.post('/ask')
async def invoke(input_query: InputQuery):

    response = await compiled_graph.ainvoke({ "original_question": input_query.query })
    if response["cache_hit"]:
        output = response["cached_response"]
    else:
        output = response["response"].content
        
    return { "response": output }

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=3000)